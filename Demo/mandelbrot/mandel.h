#pragma once
#include <cstdint>
#include <fstream>
#include <string>
#include <vector>

struct Config {
    int width = 800;
    int height = 600;
    int max_iter = 300;
    int threads = 1;
    double center = -0.75;
    double scale = 3.0;
};

inline Config parse_args(int argc, char** argv) {
    Config c;
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (i + 1 >= argc) break;
        std::string v = argv[++i];
        if (a == "-t") c.threads = std::stoi(v);
        else if (a == "-w") c.width = std::stoi(v);
        else if (a == "-h") c.height = std::stoi(v);
        else if (a == "-i") c.max_iter = std::stoi(v);
    }
    if (c.threads < 1) c.threads = 1;
    return c;
}

inline int escape(double cr, double ci, int max_iter) {
    double zr = 0.0, zi = 0.0;
    int n = 0;
    while (n < max_iter && zr * zr + zi * zi <= 4.0) {
        double t = zr * zr - zi * zi + cr;
        zi = 2.0 * zr * zi + ci;
        zr = t;
        ++n;
    }
    return n;
}

// Cùng một hàm tính cho cả bản tuần tự và bản OpenMP -> ảnh kết quả giống hệt.
inline void render_rows(std::vector<uint8_t>& img, const Config& c, int y0, int y1) {
    for (int y = y0; y < y1; ++y) {
        double ci = (y - c.height / 2.0) * (c.scale / c.height);
        for (int x = 0; x < c.width; ++x) {
            double cr = c.center + (x - c.width / 2.0) * (c.scale / c.width);
            img[(size_t)y * c.width + x] =
                (uint8_t)(255.0 * escape(cr, ci, c.max_iter) / c.max_iter);
        }
    }
}

inline void write_pgm(const std::string& path, const std::vector<uint8_t>& img,
                      const Config& c) {
    std::ofstream out(path, std::ios::binary);
    out << "P5\n" << c.width << " " << c.height << "\n255\n";
    out.write(reinterpret_cast<const char*>(img.data()), img.size());
}
