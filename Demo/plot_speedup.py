from pathlib import Path
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "mandelbrot/results.txt"
text = path.read_text(encoding="utf-8")

base = None
threads, speedups = [], []
for m in re.finditer(r"mode=(\w+)\s+threads=(\d+)\s+time=([\d.]+)", text):
    mode, t, sec = m.group(1), int(m.group(2)), float(m.group(3))
    if mode == "seq":
        base = sec
    elif base:
        threads.append(t)
        speedups.append(base / sec)

if base is None or not threads:
    sys.exit(f"Khong tim thay ket qua trong {path}")

plt.plot(threads, speedups, "o-", label="OpenMP")
plt.plot(threads, threads, "--", label="Tuyen tinh")
plt.xlabel("So luong")
plt.ylabel("Speedup")
plt.title("Mandelbrot: speedup theo so luong")
plt.legend()
plt.grid(True)
out = HERE / "speedup.png"
plt.savefig(out, dpi=150)
print(f"Da luu {out} (thoi gian tuan tu = {base:.4f} s)")
