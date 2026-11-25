#include <chrono>
#include <condition_variable>
#include <coroutine>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <latch>
#include <mutex>
#include <queue>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <vector>

class ThreadPool {
public:
    explicit ThreadPool(std::size_t num_threads) {
        workers_.reserve(num_threads);
        for (std::size_t i = 0; i < num_threads; ++i) {
            workers_.emplace_back([this] { worker_loop(); });
        }
    }

    ~ThreadPool() {
        {
            std::lock_guard lock(mtx_);
            stop_ = true;
        }
        cv_.notify_all();
    }

    ThreadPool(const ThreadPool&) = delete;
    ThreadPool& operator=(const ThreadPool&) = delete;

    struct ScheduleAwaitable {
        ThreadPool& pool;

        bool await_ready() const noexcept { return false; }

        void await_suspend(std::coroutine_handle<> handle) const {
            pool.enqueue(handle);
        }

        void await_resume() const noexcept {}
    };

    ScheduleAwaitable schedule() noexcept {
        return ScheduleAwaitable{*this};
    }

private:
    void enqueue(std::coroutine_handle<> handle) {
        {
            std::lock_guard lock(mtx_);
            tasks_.push(handle);
        }
        cv_.notify_one();
    }

    void worker_loop() {
        while (true) {
            std::coroutine_handle<> handle;
            {
                std::unique_lock lock(mtx_);
                cv_.wait(lock, [this] { return stop_ || !tasks_.empty(); });
                if (stop_ && tasks_.empty()) {
                    return;
                }
                handle = tasks_.front();
                tasks_.pop();
            }
            handle.resume();
        }
    }

    std::mutex mtx_;
    std::condition_variable cv_;
    std::queue<std::coroutine_handle<>> tasks_;
    bool stop_ = false;
    std::vector<std::jthread> workers_;
};

// Fire-and-forget coroutine whose frame self-destructs upon completion.
struct RowTask {
    struct promise_type {
        RowTask get_return_object() noexcept { return {}; }
        std::suspend_never initial_suspend() noexcept { return {}; }
        std::suspend_never final_suspend() noexcept { return {}; }
        void return_void() noexcept {}
        void unhandled_exception() noexcept { std::terminate(); }
    };
};

RowTask compute_row(ThreadPool& pool,
                    std::latch& done,
                    uint8_t* row_ptr,
                    int y,
                    int width,
                    int height,
                    int max_iter) {
    // Suspend on the caller thread and resume on a worker thread in the pool.
    co_await pool.schedule();

    constexpr double center_x = -0.6;
    constexpr double center_y = 0.0;
    const double scale = 2.4 / static_cast<double>(height);
    const double ci = center_y + (y - height * 0.5) * scale;

    uint8_t byte = 0;
    int bit_count = 0;
    std::size_t byte_idx = 0;

    for (int x = 0; x < width; ++x) {
        const double cr = center_x + (x - width * 0.5) * scale;
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

        // PBM format: 1 = black (inside Mandelbrot set), 0 = white (escaped)
        const uint8_t bit = (iter == max_iter) ? 1u : 0u;
        byte = static_cast<uint8_t>((byte << 1) | bit);

        if (++bit_count == 8) {
            row_ptr[byte_idx++] = byte;
            byte = 0;
            bit_count = 0;
        }
    }

    // Pad remaining low bits in the final byte of the row per P4 PBM spec.
    if (bit_count > 0) {
        byte = static_cast<uint8_t>(byte << (8 - bit_count));
        row_ptr[byte_idx] = byte;
    }

    done.count_down();
}

void write_pbm(const std::string& filename,
               const std::vector<uint8_t>& image,
               int width,
               int height) {
    std::ofstream out(filename, std::ios::binary);
    if (!out) {
        throw std::runtime_error("Failed to open output file: " + filename);
    }
    out << "P4\n" << width << " " << height << "\n";
    out.write(reinterpret_cast<const char*>(image.data()),
              static_cast<std::streamsize>(image.size()));
}

int main(int argc, char* argv[]) {
    std::size_t num_threads = std::thread::hardware_concurrency();
    if (num_threads == 0) {
        num_threads = 4;
    }

    int width = 1920;
    int height = 1080;
    int max_iter = 1000;
    std::string output_path = "mandelbrot.pbm";

    try {
        for (int i = 1; i < argc; ++i) {
            std::string_view arg = argv[i];
            if (arg == "-t" && i + 1 < argc) {
                num_threads = std::stoul(argv[++i]);
            } else if (arg.starts_with("-t") && arg.size() > 2) {
                num_threads = std::stoul(std::string(arg.substr(2)));
            } else if (arg == "-w" && i + 1 < argc) {
                width = std::stoi(argv[++i]);
            } else if (arg == "-h" && i + 1 < argc) {
                height = std::stoi(argv[++i]);
            } else if (arg == "-i" && i + 1 < argc) {
                max_iter = std::stoi(argv[++i]);
            } else if (arg == "-o" && i + 1 < argc) {
                output_path = argv[++i];
            } else if (arg == "--help") {
                std::cout << "Usage: " << argv[0]
                          << " [-t threads] [-w width] [-h height] [-i max_iter] [-o output.pbm]\n";
                return 0;
            } else {
                std::cerr << "Invalid or incomplete option: " << arg << "\n";
                return EXIT_FAILURE;
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Argument parsing error: " << e.what() << "\n";
        return EXIT_FAILURE;
    }

    if (num_threads == 0 || width <= 0 || height <= 0 || max_iter <= 0) {
        std::cerr << "Error: threads, width, height, and max_iter must all be positive.\n";
        return EXIT_FAILURE;
    }

    const std::size_t row_bytes = static_cast<std::size_t>((width + 7) / 8);
    std::vector<uint8_t> image(static_cast<std::size_t>(height) * row_bytes, 0);

    ThreadPool pool(num_threads);
    std::latch done(height);

    // Measure parallel computation only (excludes buffer allocation and file I/O)
    const auto start = std::chrono::steady_clock::now();

    for (int y = 0; y < height; ++y) {
        uint8_t* row_ptr = image.data() + static_cast<std::size_t>(y) * row_bytes;
        compute_row(pool, done, row_ptr, y, width, height, max_iter);
    }
    done.wait();

    const auto end = std::chrono::steady_clock::now();
    const std::chrono::duration<double, std::milli> elapsed = end - start;

    std::cout << "Threads: " << num_threads << "\n"
              << "Resolution: " << width << "x" << height << " (max_iter=" << max_iter << ")\n"
              << "Runtime (excluding I/O): " << elapsed.count() << " ms\n";

    try {
        write_pbm(output_path, image, width, height);
    } catch (const std::exception& e) {
        std::cerr << e.what() << "\n";
        return EXIT_FAILURE;
    }

    return 0;
}