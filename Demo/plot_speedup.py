import io
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
buf = io.BytesIO()
plt.savefig(buf, dpi=150, format="png")
plt.close()
out = HERE / "speedup.png"
try:
    out.write_bytes(buf.getvalue())
except OSError:
    for idx in range(1, 100):
        alt = HERE / f"speedup_{idx}.png"
        try:
            alt.write_bytes(buf.getvalue())
            print(f"(Luu y: speedup.png dang mo trong ung dung khac, da luu sang {alt.name})")
            out = alt
            break
        except OSError:
            continue
    else:
        raise
print(f"Da luu {out} (thoi gian tuan tu = {base:.4f} s)")
