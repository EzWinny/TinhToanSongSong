import os
import re
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

HERE = Path(__file__).resolve().parent
SRC = HERE / "mandelbrot"
SEQ = SRC / "mandel_seq.exe"
OMP = SRC / "mandel_omp.exe"
PAT = re.compile(r"mode=(\w+)\s+threads=(\d+)\s+time=([\d.]+)")


def compile_all():
    for name in ("mandel_seq.cpp", "mandel_omp.cpp"):
        subprocess.run(
            ["g++", "-O2", "-std=c++17", "-fopenmp", "-Wall", name,
             "-o", name.replace(".cpp", ".exe")],
            cwd=SRC, check=True,
        )
    print("Da bien dich xong.\n")


def ask_int(prompt, default):
    s = input(f"{prompt} [{default}]: ").strip()
    return int(s) if s else default


def ask_str(prompt, default):
    s = input(f"{prompt} [{default}]: ").strip()
    return s or default


def dims():
    w = ask_int("Chieu rong", 800)
    h = ask_int("Chieu cao", 600)
    it = ask_int("So vong lap", 300)
    return ["-w", w, "-h", h, "-i", it]


def run(exe, args):
    """Chay 3 lan, tra ve (thoi gian trung binh, so luong thuc te)."""
    times, threads = [], None
    for _ in range(3):
        r = subprocess.run(
            [str(exe)] + [str(a) for a in args],
            cwd=SRC, capture_output=True, text=True, check=True,
        )
        m = PAT.search(r.stdout)
        if not m:
            raise RuntimeError("Khong doc duoc ket qua: " + r.stdout)
        times.append(float(m.group(3)))
        threads = int(m.group(2))
    return sum(times) / len(times), threads


def bars(labels, values):
    top = max(values) or 1
    for label, v in zip(labels, values):
        n = round(28 * v / top)
        print(f"  {label:>6}: {'#' * n} {v:.2f}x")


def plot(xs, ys, name, title):
    plt.figure(figsize=(7, 4.5))
    plt.plot(xs, ys, "o-", label="OpenMP")
    plt.plot(xs, xs, "--", label="Tuyen tinh")
    plt.xlabel("So luong")
    plt.ylabel("Speedup")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    out = HERE / name
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Da luu {out}")


def menu_compare():
    args = dims()
    t = ask_int("So luong OpenMP", 8)
    guess = input("Theo ban OpenMP nhanh hon bao nhieu lan? ").strip()
    seq, _ = run(SEQ, args)
    omp, actual = run(OMP, args + ["-t", t])
    print(f"\nTuan tu: {seq:.4f}s | OpenMP ({actual} luong): {omp:.4f}s"
          f" | Speedup: {seq / omp:.2f}x")
    print(f"Ban doan: {guess or '(khong tra loi)'}\n")


def menu_threads():
    args = dims()
    seq, _ = run(SEQ, args)
    raw = input("Nhap cac so luong (vd: 1 2 4 8 16): ").strip() or "1 2 4 8 16"
    xs, ys, labels = [], [], []
    for t in (int(x) for x in raw.split()):
        sec, actual = run(OMP, args + ["-t", t])
        xs.append(actual)
        ys.append(seq / sec)
        labels.append(str(t))
        print(f"  -t {t:>2} -> thuc te {actual:>2} luong: {sec:.4f}s")
    bars(labels, ys)
    plot(xs, ys, "speedup.png", "Mandelbrot: speedup theo so luong")
    print("Nhac: duong phang co the la 'luon chay toan bo lo', khong phai mo rong tot.\n")


def menu_schedule():
    print("(de thay ro chenh lech: dung anh nho, nhieu vong lap)")
    args = dims()
    chunk = ask_int("Chunk size (0 = mac dinh)", 0)
    t = ask_int("So luong", 8)
    labels, times = [], []
    for s in ("static", "dynamic", "guided"):
        sec, actual = run(OMP, args + ["-t", t, "-s", s, "-b", chunk])
        labels.append(s)
        times.append(sec)
        print(f"  {s:>7}: {sec:.4f}s ({actual} luong)")
    bars(labels, [max(times) / v for v in times])
    print("Nhan xet: Mandelbrot mat can bang tu nhien -> dynamic/guided thuong tot hon static.\n")


def menu_bug():
    guess = input("Go -t 4 thi may chay bao nhieu luong? ").strip()
    args = dims()
    normal, na = run(OMP, args + ["-t", 4])
    buggy, ba = run(OMP, args + ["-t", 4, "--ignore-t"])
    print(f"\nBinh thuong     : threads={na}, {normal:.4f}s")
    print(f"Bo qua -t (loi) : threads={ba}, {buggy:.4f}s")
    print(f"Ban doan: {guess or '(khong tra loi)'}")
    print("Day chinh la loi cua ChatGPT-4 trong bao cao: co tham so nhung khong dung.\n")


def menu_image():
    which = ask_str("Xem anh seq hay omp?", "omp")
    src = SRC / f"mandel_{which}.pgm"
    if not src.exists():
        print("Chua co anh. Chay menu 1 truoc.\n")
        return
    out = HERE / "mandel_view.png"
    Image.open(src).save(out)
    os.startfile(out)
    print(f"Da mo {out}\n")


def main():
    compile_all()
    menu = {
        "1": ("So sanh tuan tu vs OpenMP", menu_compare),
        "2": ("Quet so luong + ve speedup", menu_threads),
        "3": ("Thu static / dynamic / guided", menu_schedule),
        "4": ("Che do LOI: bo qua -t", menu_bug),
        "5": ("Xem anh ket qua", menu_image),
        "6": ("Thoat", None),
    }
    while True:
        print("=== DEMO TUONG TAC: MANDELBROT SONG SONG ===")
        for k, (name, _) in menu.items():
            print(f" {k}. {name}")
        choice = input("Chon (1-6): ").strip()
        action = menu.get(choice)
        if action is None or action[1] is None:
            if choice == "6":
                return
            print("Chon khong hop le.\n")
            continue
        try:
            action[1]()
        except (subprocess.CalledProcessError, RuntimeError, ValueError) as e:
            print("Loi:", e, "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTam bien demo.")
        sys.exit(0)
