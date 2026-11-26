import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
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
RUN_ENV = os.environ.copy()


def find_omp_gxx():
    """Tim g++ ho tro OpenMP (tranh MinGW 32-bit cu thieu libpthread)."""
    candidates = []
    seen = set()

    def add(p):
        if not p:
            return
        pp = Path(p)
        key = str(pp).lower()
        if pp.is_file() and key not in seen:
            seen.add(key)
            candidates.append(pp)

    # Thu tat ca g++ co trong PATH, sau do den cac thu muc MinGW-W64 pho bien
    for d in os.environ.get("PATH", "").split(os.pathsep):
        if d:
            add(Path(d) / "g++.exe")
            add(Path(d) / "g++")
    for p in (
        r"E:\Strawberry\c\bin\g++.exe",
        r"C:\msys64\ucrt64\bin\g++.exe",
        r"C:\msys64\mingw64\bin\g++.exe",
        r"C:\mingw64\bin\g++.exe",
    ):
        add(p)
    add(shutil.which("g++"))

    probe_src = "#include <omp.h>\nint main(){return omp_get_max_threads()<1;}\n"
    with tempfile.TemporaryDirectory() as tmp:
        cpp = Path(tmp) / "probe.cpp"
        exe = Path(tmp) / "probe.exe"
        cpp.write_text(probe_src, encoding="utf-8")
        for gxx in candidates:
            env = os.environ.copy()
            env["PATH"] = str(gxx.parent) + os.pathsep + env.get("PATH", "")
            try:
                r = subprocess.run(
                    [str(gxx), "-std=c++17", "-fopenmp", str(cpp), "-o", str(exe)],
                    env=env, capture_output=True, text=True,
                )
            except OSError:
                continue
            if r.returncode == 0:
                return gxx
    raise RuntimeError(
        "Khong tim thay g++ ho tro OpenMP (-fopenmp). "
        "Hay cai MinGW-W64 (vd: MSYS2 UCRT64 hoac Strawberry C) va them vao PATH."
    )


def compile_all():
    gxx = find_omp_gxx()
    RUN_ENV["PATH"] = str(gxx.parent) + os.pathsep + os.environ.get("PATH", "")
    for name in ("mandel_seq.cpp", "mandel_omp.cpp"):
        subprocess.run(
            [str(gxx), "-O2", "-std=c++17", "-fopenmp", "-Wall", name,
             "-o", name.replace(".cpp", ".exe")],
            cwd=SRC, env=RUN_ENV, check=True,
        )
    print(f"Da bien dich xong bang: {gxx}\n")


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
            cwd=SRC, env=RUN_ENV, capture_output=True, text=True, check=True,
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


def save_bytes_safe(out: Path, data: bytes) -> Path:
    """Ghi anh an toan tren Windows (tranh Errno 22 khi anh dang mo o Photos/VS Code)."""
    try:
        out.write_bytes(data)
        return out
    except OSError:
        for idx in range(1, 100):
            alt = out.with_name(f"{out.stem}_{idx}{out.suffix}")
            try:
                alt.write_bytes(data)
                print(f"(Luu y: {out.name} dang mo trong ung dung khac, da luu sang {alt.name})")
                return alt
            except OSError:
                continue
        raise


def save_current_fig(name: str) -> Path:
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close()
    return save_bytes_safe(HERE / name, buf.getvalue())


def plot(xs, ys, name, title):
    plt.figure(figsize=(7, 4.5))
    plt.plot(xs, ys, "o-", label="OpenMP")
    plt.plot(xs, xs, "--", label="Tuyen tinh")
    plt.xlabel("So luong")
    plt.ylabel("Speedup")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    out = save_current_fig(name)
    print(f"Da luu {out}")


def safe_div(a, b):
    return a / b if b > 0 else 0.0


def menu_compare():
    args = dims()
    t = ask_int("So luong OpenMP", 8)
    guess = input("Theo ban OpenMP nhanh hon bao nhieu lan? ").strip()
    seq, _ = run(SEQ, args)
    omp, actual = run(OMP, args + ["-t", t])
    print(f"\nTuan tu: {seq:.4f}s | OpenMP ({actual} luong): {omp:.4f}s"
          f" | Speedup: {safe_div(seq, omp):.2f}x")
    print(f"Ban doan: {guess or '(khong tra loi)'}\n")


def menu_threads():
    args = dims()
    seq, _ = run(SEQ, args)
    raw = input("Nhap cac so luong (vd: 1 2 4 8 16): ").strip() or "1 2 4 8 16"
    req_list = [int(x) for x in re.split(r"[\s,]+", raw) if x]
    xs, ys, labels = [], [], []
    for t in req_list:
        sec, actual = run(OMP, args + ["-t", t])
        xs.append(actual)
        ys.append(safe_div(seq, sec))
        labels.append(str(t))
        print(f"  -t {t:>2} -> thuc te {actual:>2} luong: {sec:.4f}s")
    bars(labels, ys)
    plot(xs, ys, "speedup.png", "Mandelbrot: speedup theo so luong")
    print("Nhac: duong phang co the la 'luon chay toan bo loi', khong phai mo rong tot.\n")


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
    bars(labels, [safe_div(max(times), v) for v in times])
    print("Nhan xet: Mandelbrot mat can bang tu nhien -> dynamic/guided thuong tot hon static.\n")


def menu_bug():
    guess = input("Go -t 4 thi may chay bao nhieu luong? ").strip()
    args = dims()
    seq, _ = run(SEQ, args)
    req_list = [1, 2, 4, 8]
    ys_ok, ys_bug = [], []
    print("\nQuet -t 1, 2, 4, 8 (Binh thuong vs Bo qua -t):")
    for t in req_list:
        normal, na = run(OMP, args + ["-t", t])
        buggy, ba = run(OMP, args + ["-t", t, "--ignore-t"])
        ys_ok.append(safe_div(seq, normal))
        ys_bug.append(safe_div(seq, buggy))
        print(f"  -t {t}: binh thuong ({na:>2} luong) {normal:.4f}s [{ys_ok[-1]:.2f}x]"
              f" | loi ({ba:>2} luong) {buggy:.4f}s [{ys_bug[-1]:.2f}x]")
    plt.figure(figsize=(7, 4.5))
    plt.plot(req_list, ys_ok, "o-", label="Binh thuong (ton trong -t)")
    plt.plot(req_list, ys_bug, "s--", label="Bo qua -t (duong phang)")
    plt.xlabel("Tham so -t yeu cau")
    plt.ylabel("Speedup so voi tuan tu")
    plt.title("Che do LOI: co tham so -t nhung khong dung")
    plt.legend()
    plt.grid(True)
    out = save_current_fig("speedup.png")
    print(f"Da luu bieu do duong phang tai {out}")
    print(f"Ban doan: {guess or '(khong tra loi)'}")
    print("Day chinh la loi cua ChatGPT-4 trong bao cao: co tham so nhung khong dung.\n")


def menu_image():
    which = ask_str("Xem anh seq hay omp?", "omp").lower()
    if which not in ("seq", "omp"):
        print("Chi ho tro 'seq' hoac 'omp'.\n")
        return
    src = SRC / f"mandel_{which}.pgm"
    if not src.exists():
        print("Chua co anh. Chay menu 1 truoc.\n")
        return
    buf = io.BytesIO()
    with Image.open(src) as img:
        img.save(buf, format="PNG")
    out = save_bytes_safe(HERE / "mandel_view.png", buf.getvalue())
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
        except (subprocess.CalledProcessError, RuntimeError, ValueError, ZeroDivisionError, OSError) as e:
            print("Loi:", e, "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTam biet demo.")
        sys.exit(0)
