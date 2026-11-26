#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <execution>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <string>
#include <thread>
#include <vector>

#if defined(__has_include)
#  if __has_include(<tbb/global_control.h>)
#    include <tbb/global_control.h>
#    define HAS_TBB 1
#  endif
#endif

#if !defined(HAS_TBB) && defined(_MSC_VER)
#  include <concrt.h>
#  define HAS_CONCRT 1
#endif

struct Config {
    int threads = static_cast<int>(std::max(1u, std::thread::hardware_concurrency()));
    int width = 1920;
    int height = 1080;
    int max_iter = 1000;
    std::string output = "mandelbrot.pbm";
};

void print_usage(const char* prog) {
    std::cerr << "Usage: " << prog << " [-t threads] [-w width] [-h height] [-i max_iter] [-o output.pbm]\n";
}

Config parse_args(int argc, char* argv[]) {
    Config cfg;
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        auto next_val = [&](const char* flag) -> std::string {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for " << flag << "\n";
                print_usage(argv[0]);
                std::exit(EXIT_FAILURE);
            }
            return argv[++i];
        };

        if (arg == "-t") {
            cfg.threads = std::stoi(next_val("-t"));
        } else if (arg == "-w") {
            cfg.width = std::stoi(next_val("-w"));
        } else if (arg == "-h") {
            cfg.height = std::stoi(next_val("-h"));
        } else if (arg == "-i") {
            cfg.max_iter = std::stoi(next_val("-i"));
        } else if (arg == "-o") {
            cfg.output = next_val("-o");
        } else {
            print_usage(argv[0]);
            std::exit(EXIT_FAILURE);
        }
    }

    if (cfg.threads < 1 || cfg.width < 1 || cfg.height < 1 || cfg.max_iter < 1) {
        std::cerr << "Error: threads, width, height, and max_iter must be positive integers.\n";
        std::exit(EXIT_FAILURE);
    }
    return cfg;
}

inline uint8_t mandelbrot_pixel(double cx, double cy, int max_iter) noexcept {
    // Period-2 bulb check
    const double dx = cx + 1.0;
    if (dx * dx + cy * cy < 0.0625) {
        return 1;
    }
    // Main cardioid check
    const double qx = cx - 0.25;
    const double q = qx * qx + cy * cy;
    if (q * (q + qx) <= 0.25 * cy * cy) {
        return 1;
    }

    double zr = 0.0;
    double zi = 0.0;
    double zr2 = 0.0;
    double zi2 = 0.0;
    int iter = 0;

    while (zr2 + zi2 <= 4.0 && iter < max_iter) {
        zi = 2.0 * zr * zi + cy;
        zr = zr2 - zi2 + cx;
        zr2 = zr * zr;
        zi2 = zi * zi;
        ++iter;
    }
    return (iter == max_iter) ? 1 : 0;
}

void write_pbm_binary(const std::string& filename, const std::vector<uint8_t>& pixels, int width, int height) {
    std::ofstream out(filename, std::ios::binary);
    if (!out) {
        std::cerr << "Failed to open output file: " << filename << "\n";
        std::exit(EXIT_FAILURE);
    }

    out << "P4\n" << width << " " << height << "\n";

    const int row_bytes = (width + 7) / 8;
    std::vector<uint8_t> packed(static_cast<size_t>(height) * row_bytes, 0);

    for (int y = 0; y < height; ++y) {
        const uint8_t* src = &pixels[static_cast<size_t>(y) * width];
        uint8_t* dst = &packed[static_cast<size_t>(y) * row_bytes];
        for (int x = 0; x < width; ++x) {
            if (src[x]) {
                dst[x >> 3] |= static_cast<uint8_t>(1u << (7 - (x & 7)));
            }
        }
    }

    out.write(reinterpret_cast<const char*>(packed.data()),
              static_cast<std::streamsize>(packed.size()));
}

int main(int argc, char* argv[]) {
    const Config cfg = parse_args(argc, argv);

    // Configure the backend thread pool used by C++17 <execution>
#if defined(HAS_TBB)
    tbb::global_control tbb_limit(tbb::global_control::max_allowed_parallelism,
                                  static_cast<size_t>(cfg.threads));
#elif defined(HAS_CONCRT)
    Concurrency::SchedulerPolicy policy(2,
        Concurrency::MinConcurrency, cfg.threads,
        Concurrency::MaxConcurrency, cfg.threads);
    Concurrency::CurrentScheduler::Create(policy);
#else
    if (cfg.threads > 1) {
        std::cerr << "Warning: No TBB or ConcRT backend detected; -t may be ignored.\n";
    }
#endif

    // Preserve aspect ratio while keeping [-2.15, 0.85] x [-1.2, 1.2] in frame
    double x_span = 3.0;
    double y_span = x_span * static_cast<double>(cfg.height) / static_cast<double>(cfg.width);
    if (y_span < 2.4) {
        y_span = 2.4;
        x_span = y_span * static_cast<double>(cfg.width) / static_cast<double>(cfg.height);
    }
    const double x_min = -0.65 - 0.5 * x_span;
    const double y_min = -0.5 * y_span;
    const double step = x_span / static_cast<double>(cfg.width);

    std::vector<uint8_t> pixels(static_cast<size_t>(cfg.width) * cfg.height);
    std::vector<int> rows(cfg.height);
    std::iota(rows.begin(), rows.end(), 0);

    // Measure computation runtime only (excluding allocation and file I/O)
    const auto t_start = std::chrono::steady_clock::now();

    std::for_each(std::execution::par_unseq, rows.begin(), rows.end(), [&](int y) {
        const double cy = y_min + static_cast<double>(y) * step;
        uint8_t* row_ptr = &pixels[static_cast<size_t>(y) * cfg.width];
        for (int x = 0; x < cfg.width; ++x) {
            const double cx = x_min + static_cast<double>(x) * step;
            row_ptr[x] = mandelbrot_pixel(cx, cy, cfg.max_iter);
        }
    });

    const auto t_end = std::chrono::steady_clock::now();
    const double elapsed_ms = std::chrono::duration<double, std::milli>(t_end - t_start).count();

#if defined(HAS_CONCRT)
    Concurrency::CurrentScheduler::Detach();
#endif

    std::cout << "Threads: " << cfg.threads
              << " | Resolution: " << cfg.width << "x" << cfg.height
              << " | Compute time (excluding IO): "
              << std::fixed << std::setprecision(3) << elapsed_ms << " ms\n";

    write_pbm_binary(cfg.output, pixels, cfg.width, cfg.height);
    return 0;
}