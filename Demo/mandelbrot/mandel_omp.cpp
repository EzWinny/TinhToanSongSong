#include "mandel.h"
#include <chrono>
#include <iostream>
#include <omp.h>

int main(int argc, char** argv) {
    Config c = parse_args(argc, argv);
    omp_set_num_threads(c.threads);
    std::vector<uint8_t> img((size_t)c.width * c.height);

    auto t0 = std::chrono::steady_clock::now();
    #pragma omp parallel for schedule(dynamic)
    for (int y = 0; y < c.height; ++y)
        render_rows(img, c, y, y + 1);
    auto t1 = std::chrono::steady_clock::now();

    double sec = std::chrono::duration<double>(t1 - t0).count();
    write_pgm("mandel_omp.pgm", img, c);  // I/O nằm ngoài phép đo
    std::cout << "mode=omp threads=" << omp_get_max_threads() << " time=" << sec << "\n";
}
