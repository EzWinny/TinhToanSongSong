#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <future>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

namespace {

int compute_point(double cr, double ci, int max_iter) {
    double zr = 0.0;
    double zi = 0.0;
    double zr2 = 0.0;
    double zi2 = 0.0;
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

void print_usage(const char* prog) {
    std::cerr << "Usage: " << prog
              << " [-t threads] [-w width] [-h height] [-i max_iter] [-o output.pbm]\n";
}

} // namespace

int main(int argc, char* argv[]) {
    unsigned int hw_threads = std::thread::hardware_concurrency();
    int num_threads = (hw_threads > 0) ? static_cast<int>(hw_threads) : 4;
    int width = 1920;
    int height = 1080;
    int max_iter = 1000;
    std::string output_file = "mandelbrot.pbm";

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        auto require_int = [&](const std::string& flag) -> int {
            if (i + 1 >= argc) {
                throw std::invalid_argument("Missing value for " + flag);
            }
            return std::stoi(argv[++i]);
        };

        try {
            if (arg == "-t") {
                num_threads = require_int("-t");
            } else if (arg == "-w") {
                width = require_int("-w");
            } else if (arg == "-h") {
                height = require_int("-h");
            } else if (arg == "-i") {
                max_iter = require_int("-i");
            } else if (arg == "-o") {
                if (i + 1 >= argc) {
                    throw std::invalid_argument("Missing value for -o");
                }
                output_file = argv[++i];
            } else if (arg == "--help") {
                print_usage(argv[0]);
                return 0;
            } else {
                std::cerr << "Unknown option: " << arg << "\n";
                print_usage(argv[0]);
                return 1;
            }
        } catch (const std::exception& e) {
            std::cerr << "Argument error (" << arg << "): " << e.what() << "\n";
            return 1;
        }
    }

    if (num_threads < 1 || width < 1 || height < 1 || max_iter < 1) {
        std::cerr << "Error: threads, width, height, and max_iter must be >= 1.\n";
        return 1;
    }

    // Binary PBM (P4) packs 8 pixels per byte (MSB first), padded at the end of each row
    const int row_bytes = (width + 7) / 8;
    std::vector<uint8_t> image(static_cast<size_t>(height) * row_bytes, 0);

    // Complex plane coordinates with aspect-ratio preservation
    const double x_min = -2.0;
    const double x_max = 1.0;
    const double x_span = x_max - x_min;
    const double y_span = x_span * (static_cast<double>(height) / width);
    const double y_min = -y_span / 2.0;

    const double dx = x_span / width;
    const double dy = y_span / height;

    std::atomic<int> next_row(0);

    auto worker = [&]() {
        int y = 0;
        while ((y = next_row.fetch_add(1, std::memory_order_relaxed)) < height) {
            const double ci = y_min + y * dy;
            uint8_t* row_ptr = &image[static_cast<size_t>(y) * row_bytes];

            for (int x = 0; x < width; ++x) {
                const double cr = x_min + x * dx;
                if (compute_point(cr, ci, max_iter) == max_iter) {
                    row_ptr[x >> 3] |= static_cast<uint8_t>(1u << (7 - (x & 7)));
                }
            }
        }
    };

    // Time only the parallel computation (excluding file I/O)
    const auto start_time = std::chrono::steady_clock::now();

    std::vector<std::future<void>> futures;
    futures.reserve(static_cast<size_t>(num_threads));
    for (int t = 0; t < num_threads; ++t) {
        futures.emplace_back(std::async(std::launch::async, worker));
    }

    for (auto& fut : futures) {
        fut.get();
    }

    const auto end_time = std::chrono::steady_clock::now();
    const std::chrono::duration<double, std::milli> elapsed_ms = end_time - start_time;

    std::cout << "Threads: " << num_threads
              << " | Resolution: " << width << "x" << height
              << " | Compute time (excluding I/O): " << elapsed_ms.count() << " ms\n";

    // Write binary PBM (P4) output
    std::ofstream out(output_file, std::ios::binary);
    if (!out) {
        std::cerr << "Error: Could not open " << output_file << " for writing.\n";
        return 1;
    }

    out << "P4\n" << width << " " << height << "\n";
    out.write(reinterpret_cast<const char*>(image.data()),
              static_cast<std::streamsize>(image.size()));

    if (!out) {
        std::cerr << "Error: Failed while writing image data to " << output_file << ".\n";
        return 1;
    }

    return 0;
}