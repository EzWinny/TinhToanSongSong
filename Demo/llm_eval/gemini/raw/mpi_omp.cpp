// mandelbrot_mpi_omp.cpp
#include <mpi.h>
#include <omp.h>
#include <unistd.h>

#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

struct RowTask {
    int global_y;
    std::size_t local_byte_offset;
};

static inline int mandelbrot_iterations(double cr, double ci, int max_iter) {
    double zr = 0.0, zi = 0.0;
    double zr2 = 0.0, zi2 = 0.0;
    int iter = 0;

    while (zr2 + zi2 <= 4.0 && iter < max_iter) {
        zi = 2.0 * zr * zi + ci;
        zr = zr2 - zi2 + cr;
        zr2 = zr * zr;
        zi2 = zi * zi;
        ++iter;
    }
    return iter;
}

static void print_usage(const char* prog) {
    std::cerr << "Usage: " << prog << " [options]\n"
              << "  -p <int>   Number of row partitions (default: MPI world size)\n"
              << "  -w <int>   Image width in pixels (default: 2048)\n"
              << "  -h <int>   Image height in pixels (default: 2048)\n"
              << "  -i <int>   Maximum iterations (default: 1000)\n"
              << "  -o <file>  Output PBM filename (default: mandelbrot.pbm)\n";
}

int main(int argc, char** argv) {
    int provided = 0;
    MPI_Init_thread(&argc, &argv, MPI_THREAD_FUNNELED, &provided);

    int rank = 0, world_size = 1;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);

    int num_partitions = world_size;
    int width = 2048;
    int height = 2048;
    int max_iter = 1000;
    std::string output_file = "mandelbrot.pbm";

    int opt;
    while ((opt = getopt(argc, argv, "p:w:h:i:o:")) != -1) {
        switch (opt) {
            case 'p':
                num_partitions = std::atoi(optarg);
                break;
            case 'w':
                width = std::atoi(optarg);
                break;
            case 'h':
                height = std::atoi(optarg);
                break;
            case 'i':
                max_iter = std::atoi(optarg);
                break;
            case 'o':
                output_file = optarg;
                break;
            default:
                if (rank == 0) print_usage(argv[0]);
                MPI_Finalize();
                return 1;
        }
    }

    if (num_partitions <= 0 || width <= 0 || height <= 0 || max_iter <= 0) {
        if (rank == 0) {
            std::cerr << "Error: -p, -w, -h, and -i must all be positive integers.\n";
            print_usage(argv[0]);
        }
        MPI_Finalize();
        return 1;
    }

    // Clamp partitions so no partition has zero rows
    num_partitions = std::min(num_partitions, height);

    // PBM P4 packs 8 pixels per byte, padded to a byte boundary at the end of each row
    const std::size_t row_bytes = static_cast<std::size_t>((width + 7) / 8);

    auto partition_start = [&](int p) -> int {
        return static_cast<int>((static_cast<long long>(p) * height) / num_partitions);
    };
    auto partition_end = [&](int p) -> int {
        return static_cast<int>((static_cast<long long>(p + 1) * height) / num_partitions);
    };

    // Assign partitions across MPI ranks in a block-cyclic fashion (p % world_size)
    std::vector<RowTask> local_tasks;
    for (int p = rank; p < num_partitions; p += world_size) {
        int y0 = partition_start(p);
        int y1 = partition_end(p);
        for (int y = y0; y < y1; ++y) {
            local_tasks.push_back({y, local_tasks.size() * row_bytes});
        }
    }

    std::vector<std::uint8_t> local_buf(local_tasks.size() * row_bytes, 0);

    // Prepare MPI_Gatherv metadata on rank 0
    std::vector<int> recv_counts;
    std::vector<int> displs;
    std::vector<std::uint8_t> gathered_buf;

    if (rank == 0) {
        recv_counts.resize(world_size, 0);
        displs.resize(world_size, 0);
        for (int p = 0; p < num_partitions; ++p) {
            int owner = p % world_size;
            int rows = partition_end(p) - partition_start(p);
            recv_counts[owner] += static_cast<int>(rows * row_bytes);
        }
        int total_bytes = 0;
        for (int r = 0; r < world_size; ++r) {
            displs[r] = total_bytes;
            total_bytes += recv_counts[r];
        }
        gathered_buf.resize(static_cast<std::size_t>(total_bytes));
    }

    // Complex plane bounds centered around the Mandelbrot set
    const double x_min = -2.0;
    const double x_max = 1.0;
    const double x_scale = (x_max - x_min) / static_cast<double>(width);
    const double y_span = (x_max - x_min) * (static_cast<double>(height) / static_cast<double>(width));
    const double y_min = -0.5 * y_span;
    const double y_scale = y_span / static_cast<double>(height);

    // Synchronize all ranks and start timer (excludes file I/O)
    MPI_Barrier(MPI_COMM_WORLD);
    const double t_start = MPI_Wtime();

    // Dynamic OpenMP scheduling balances uneven iteration counts across rows
    #pragma omp parallel for schedule(dynamic, 1)
    for (std::size_t idx = 0; idx < local_tasks.size(); ++idx) {
        const int y = local_tasks[idx].global_y;
        const double ci = y_min + (static_cast<double>(y) + 0.5) * y_scale;
        std::uint8_t* row_ptr = &local_buf[local_tasks[idx].local_byte_offset];

        for (int byte_idx = 0; byte_idx < static_cast<int>(row_bytes); ++byte_idx) {
            std::uint8_t packed_byte = 0;
            const int x_base = byte_idx * 8;
            const int bits_in_byte = std::min(8, width - x_base);

            for (int bit = 0; bit < bits_in_byte; ++bit) {
                const int x = x_base + bit;
                const double cr = x_min + (static_cast<double>(x) + 0.5) * x_scale;
                const int iter = mandelbrot_iterations(cr, ci, max_iter);

                // In PBM, 1 represents black (inside the set) and 0 represents white
                if (iter == max_iter) {
                    packed_byte |= static_cast<std::uint8_t>(1U << (7 - bit));
                }
            }
            row_ptr[byte_idx] = packed_byte;
        }
    }

    // Gather computed partitions onto rank 0
    std::uint8_t dummy = 0;
    const std::uint8_t* send_ptr = local_buf.empty() ? &dummy : local_buf.data();
    std::uint8_t* recv_ptr = (rank == 0 && !gathered_buf.empty()) ? gathered_buf.data() : nullptr;

    MPI_Gatherv(
        send_ptr,
        static_cast<int>(local_buf.size()),
        MPI_BYTE,
        recv_ptr,
        rank == 0 ? recv_counts.data() : nullptr,
        rank == 0 ? displs.data() : nullptr,
        MPI_BYTE,
        0,
        MPI_COMM_WORLD
    );

    // Reorder cyclic partitions into contiguous image rows on rank 0
    std::vector<std::uint8_t> image_buf;
    if (rank == 0) {
        image_buf.resize(static_cast<std::size_t>(height) * row_bytes);
        for (int r = 0; r < world_size; ++r) {
            std::size_t src_offset = static_cast<std::size_t>(displs[r]);
            for (int p = r; p < num_partitions; p += world_size) {
                const int y0 = partition_start(p);
                const int y1 = partition_end(p);
                const std::size_t part_bytes = static_cast<std::size_t>(y1 - y0) * row_bytes;
                const std::size_t dst_offset = static_cast<std::size_t>(y0) * row_bytes;

                std::memcpy(&image_buf[dst_offset], &gathered_buf[src_offset], part_bytes);
                src_offset += part_bytes;
            }
        }
    }

    MPI_Barrier(MPI_COMM_WORLD);
    const double t_end = MPI_Wtime();

    if (rank == 0) {
        std::cout << "Runtime (excluding I/O): " << (t_end - t_start) << " s\n";

        // Write binary PBM (P4) output after timing ends
        std::ofstream out(output_file, std::ios::binary);
        if (!out) {
            std::cerr << "Error: Failed to open output file " << output_file << "\n";
            MPI_Abort(MPI_COMM_WORLD, 1);
        }
        out << "P4\n" << width << " " << height << "\n";
        out.write(reinterpret_cast<const char*>(image_buf.data()),
                  static_cast<std::streamsize>(image_buf.size()));
    }

    MPI_Finalize();
    return 0;
}