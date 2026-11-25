#include "mandel.h"
#include <chrono>
#include <iostream>

int main(int argc, char** argv) {
    Config c = parse_args(argc, argv);
    std::vector<uint8_t> img((size_t)c.width * c.height);

    auto t0 = std::chrono::steady_clock::now();
    render_rows(img, c, 0, c.height);
    auto t1 = std::chrono::steady_clock::now();

    double sec = std::chrono::duration<double>(t1 - t0).count();
    write_pgm("mandel_seq.pgm", img, c);  // I/O nằm ngoài phép đo
    std::cout << "mode=seq threads=1 time=" << sec << "\n";
}
