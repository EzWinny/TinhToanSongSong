#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <omp.h>
#include <string>
#include <vector>

void write_pbm(const std::string& filename, const std::vector<uint8_t>& pixels, int width, int height) {
    std::ofstream out(filename, std::ios::binary);
    if (!out) {
        std::cerr << "Error: Could not open output file " << filename << "\n";
        std::exit(1);
    }

    // P4 is the binary Portable Bitmap (PBM) format (1 = black, 0 = white)
    out << "P4\n" << width << " " << height << "\n";

    const int row_bytes = (width + 7) / 8;
    std::vector<uint8_t> row_buffer(row_bytes);

    for (int py = 0; py < height; ++py) {
        std::fill(row_buffer.begin(), row_buffer.end(), 0);
        const size_t row_offset = static_cast<size_t>(py) * width;

        for (int px = 0; px < width; ++px) {
            if (pixels[row_offset + px]) {
                row_buffer[px / 8] |= static_cast<uint8_t>(1u << (7 - (px % 8)));
            }
        }
        out.write(reinterpret_cast<const char*>(row_buffer.data()), row_bytes);
    }
}

int main(int argc, char* argv[]) {
    int num_threads = omp_get_max_threads();
    int width = 2048;
    int height = 2048;
    int max_iter = 1000;
    std::string output_file = "mandelbrot.pbm";

    // Parse command-line arguments
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "-t" && i + 1 < argc) {
            num_threads = std::atoi(argv[++i]);
        } else if (arg.rfind("-t", 0) == 0 && arg.size() > 2) {
            num_threads = std::atoi(arg.substr(2).c_str());
        } else if (arg == "-w" && i + 1 < argc) {
            width = std::atoi(argv[++i]);
        } else if (arg == "-h" && i + 1 < argc) {
            height = std::atoi(argv[++i]);
        } else if (arg == "-m" && i + 1 < argc) {
            max_iter = std::atoi(argv[++i]);
        } else if (arg == "-o" && i + 1 < argc) {
            output_file = argv[++i];
        } else {
            std::cerr << "Usage: " << argv[0]
                      << " [-t threads] [-w width] [-h height] [-m max_iter] [-o output.pbm]\n";
            return 1;
        }
    }

    if (num_threads <= 0 || width <= 0 || height <= 0 || max_iter <= 0) {
        std::cerr << "Error: Threads, dimensions, and max iterations must be positive integers.\n";
        return 1;
    }

    omp_set_num_threads(num_threads);

    // Complex plane bounds (1:1 aspect ratio)
    const double x_min = -2.0;
    const double x_max = 1.0;
    const double y_min = -1.5;
    const double y_max = 1.5;

    std::vector<uint8_t> pixels(static_cast<size_t>(width) * height, 0);

    const double dx = (width > 1) ? (x_max - x_min) / (width - 1) : 0.0;
    const double dy = (height > 1) ? (y_max - y_min) / (height - 1) : 0.0;

    // Start timing (compute only, excluding I/O)
    const double start_time = omp_get_wtime();

    #pragma omp parallel for num_threads(num_threads) schedule(dynamic, 1)
    for (int py = 0; py < height; ++py) {
        const double y0 = y_min + py * dy;
        const size_t row_offset = static_cast<size_t>(py) * width;

        for (int px = 0; px < width; ++px) {
            const double x0 = x_min + px * dx;

            double x = 0.0;
            double y = 0.0;
            double x2 = 0.0;
            double y2 = 0.0;
            int iter = 0;

            while (x2 + y2 <= 4.0 && iter < max_iter) {
                y = 2.0 * x * y + y0;
                x = x2 - y2 + x0;
                x2 = x * x;
                y2 = y * y;
                ++iter;
            }

            pixels[row_offset + px] = (iter == max_iter) ? 1 : 0;
        }
    }

    const double elapsed_seconds = omp_get_wtime() - start_time;

    std::cout << "Threads: " << num_threads << "\n"
              << "Compute time (excluding I/O): " << std::fixed << std::setprecision(6)
              << elapsed_seconds << " s\n";

    // Write image to disk after stopping the timer
    write_pbm(output_file, pixels, width, height);

    return 0;
}