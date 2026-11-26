"""Cong cu danh gia tu dong ma C++ Mandelbrot do LLM sinh tren may cuc bo.

Chay tu thu muc Demo/:
  python eval_llm.py --init <model_name>
  python eval_llm.py <model_name> [--stage raw|fixed] [--threads 1 2 4 8 12]
"""

import argparse
import json
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

HERE = Path(__file__).resolve().parent
EVAL_ROOT = HERE / "llm_eval"
REF_DIR = HERE / "mandelbrot"

VARIANTS = [
    ("async", "async.cpp", "C++11 std::async", ["-O2", "-std=c++17", "-Wall", "-Wextra"]),
    ("par_algo", "par_algo.cpp", "C++17 parallel algorithms", ["-O2", "-std=c++17", "-Wall", "-Wextra"]),
    ("coroutine", "coroutine.cpp", "C++20 coroutines", ["-O2", "-std=c++20", "-Wall", "-Wextra"]),
    ("openmp", "openmp.cpp", "OpenMP", ["-O2", "-std=c++17", "-fopenmp", "-Wall", "-Wextra"]),
    ("mpi_omp", "mpi_omp.cpp", "MPI+OpenMP", ["-O2", "-std=c++17", "-fopenmp", "-Wall", "-Wextra"]),
]


def find_working_gxx():
    """Tim g++ MinGW-W64 ho tro OpenMP + C++20."""
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

    probe = "#include <omp.h>\n#include <coroutine>\nint main(){return omp_get_max_threads()<1;}\n"
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "probe.cpp"
        exe = Path(tmp) / "probe.exe"
        src.write_text(probe, encoding="utf-8")
        for gxx in candidates:
            env = os.environ.copy()
            env["PATH"] = str(gxx.parent) + os.pathsep + env.get("PATH", "")
            try:
                r = subprocess.run(
                    [str(gxx), "-std=c++20", "-fopenmp", str(src), "-o", str(exe)],
                    env=env, capture_output=True, text=True, timeout=15,
                )
            except (OSError, subprocess.TimeoutExpired):
                continue
            if r.returncode == 0:
                ver = subprocess.run(
                    [str(gxx), "--version"], env=env, capture_output=True, text=True
                ).stdout.splitlines()[0].strip()
                has_tbb = check_tbb(gxx, env)
                return gxx, ver, env, has_tbb
    raise RuntimeError("Khong tim thay g++ ho tro C++20 va OpenMP (-fopenmp).")


def check_tbb(gxx, env):
    probe = "#include <tbb/global_control.h>\nint main(){return 0;}\n"
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "tbb_probe.cpp"
        exe = Path(tmp) / "tbb_probe.exe"
        src.write_text(probe, encoding="utf-8")
        try:
            r = subprocess.run(
                [str(gxx), "-std=c++17", str(src), "-ltbb", "-o", str(exe)],
                env=env, capture_output=True, text=True, timeout=15,
            )
            return r.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False


def parse_reported_time(stdout):
    """Trich thoi gian tinh toan (giay) tu stdout cua chuong trinh LLM."""
    text = stdout.strip()
    if not text:
        return None
    patterns = [
        (r"time\s*[:=]\s*([\d.]+(?:e[+-]?\d+)?)\s*(ms|us|µs|s|sec|seconds)?", True),
        (r"(?:runtime|elapsed|compute|duration)[^0-9\n]*([\d.]+(?:e[+-]?\d+)?)\s*(ms|us|µs|s|sec|seconds)?", True),
        (r"([\d.]+(?:e[+-]?\d+)?)\s*(ms|us|µs|seconds|sec|s)\b", True),
    ]
    for pat, has_unit in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = float(m.group(1))
            unit = (m.group(2) or "s").lower() if has_unit else "s"
            if unit == "ms":
                return val / 1e3
            if unit in ("us", "µs"):
                return val / 1e6
            return val
    # Fallback: dong chi chua 1 so thuc
    for line in text.splitlines():
        m = re.fullmatch(r"\s*([\d.]+(?:e[+-]?\d+)?)\s*", line)
        if m:
            return float(m.group(1))
    return None


def inspect_netpbm(path, preview_out=None):
    """Kiem tra header Netpbm (P1-P6), kich thuoc va phat hien anh den toan bo."""
    raw = path.read_bytes()
    info = {"file": path.name, "bytes": len(raw), "valid": False, "issue": None}
    if len(raw) < 6 or raw[0:1] != b"P" or raw[1:2] not in b"123456":
        info["issue"] = "Magic header khong phai P1-P6"
        return info

    magic = raw[:2].decode("ascii")
    info["magic"] = magic

    # Doc cac token header (bo qua comment bat dau bang #)
    tokens = []
    pos = 2
    n = len(raw)
    need = 2 if magic in ("P1", "P4") else 3
    while len(tokens) < need and pos < n:
        while pos < n and raw[pos] in b" \t\r\n":
            pos += 1
        if pos < n and raw[pos:pos + 1] == b"#":
            while pos < n and raw[pos:pos + 1] != b"\n":
                pos += 1
            continue
        start = pos
        while pos < n and raw[pos] not in b" \t\r\n#":
            pos += 1
        if pos > start:
            tokens.append(raw[start:pos].decode("ascii", errors="replace"))
    if len(tokens) < need:
        info["issue"] = "Header Netpbm bi thieu truong"
        return info
    try:
        w, h = int(tokens[0]), int(tokens[1])
        maxval = int(tokens[2]) if need == 3 else 1
    except ValueError:
        info["issue"] = f"Header khong hop le: {tokens}"
        return info

    info["width"] = w
    info["height"] = h
    info["maxval"] = maxval
    if w <= 0 or h <= 0:
        info["issue"] = f"Kich thuoc khong hop le ({w}x{h})"
        return info

    # Bo 1 ky tu whitespace sau header doi voi dinh dang nhi phan
    if pos < n and raw[pos] in b" \t\r\n":
        pos += 1
    payload = raw[pos:]

    if magic == "P4":
        expected = ((w + 7) // 8) * h
        if len(payload) < expected:
            info["issue"] = f"Thieu du lieu P4: co {len(payload)}B, can {expected}B"
            return info
        if len(payload) > expected * 4:
            info["issue"] = f"Du lieu qua lon cho P4 ({len(payload)}B vs {expected}B) - nghi ngo ghi P5 vao P4"
    elif magic == "P5":
        bpp = 1 if maxval < 256 else 2
        expected = w * h * bpp
        if len(payload) < expected:
            info["issue"] = f"Thieu du lieu P5: co {len(payload)}B, can {expected}B"
            return info
    elif magic == "P6":
        bpp = 3 if maxval < 256 else 6
        expected = w * h * bpp
        if len(payload) < expected:
            info["issue"] = f"Thieu du lieu P6: co {len(payload)}B, can {expected}B"
            return info

    # Dung Pillow de doc va kiem tra co bi den/dong nhat toan bo khong
    try:
        with Image.open(path) as im:
            gray = im.convert("L")
            lo, hi = gray.getextrema()
            hist = gray.histogram()
            distinct = sum(1 for c in hist if c > 0)
            info["pixel_min"] = lo
            info["pixel_max"] = hi
            info["distinct_levels"] = distinct
            if lo == hi:
                info["issue"] = f"Anh dong nhat (tat ca pixel = {lo}, anh den/trang toan bo)"
            else:
                info["valid"] = True
            if preview_out is not None:
                im.save(preview_out)
                info["preview"] = preview_out.name
    except Exception as e:
        info["issue"] = f"Pillow khong doc duoc anh: {e}"
    return info


def static_audit(variant, code):
    """Kiem duyet tinh theo danh muc Bang 10 cua bao cao."""
    notes = []
    if variant == "par_algo":
        if "std::execution::par" not in code and "execution::par" not in code:
            notes.append("Thieu std::execution::par")
        if "tbb::global_control" in code:
            notes.append("Co dung tbb::global_control")
        elif "OMP_NUM_THREADS" in code or "OPENMP_NUM_THREADS" in code:
            notes.append("Nghi ngo nham backend: dat bien OpenMP cho C++17 parallel algorithms")
        else:
            notes.append("Khong thay API TBB gioi han so luong")
    elif variant == "coroutine":
        if "final_suspend" in code:
            if "suspend_never" in code and "done()" in code:
                notes.append("Canh bao: co ca suspend_never lan done() (nguy co treo/UB)")
        else:
            notes.append("Khong thay final_suspend")
        if "co_return" in code and "return_void" not in code and "return_value" not in code:
            notes.append("Canh bao: dung co_return nhung thieu return_void/return_value")
    elif variant == "mpi_omp":
        if "MPI_Init" not in code:
            notes.append("Thieu MPI_Init/MPI_Init_thread")
        if "#pragma omp" not in code:
            notes.append("Thieu chi thi OpenMP (#pragma omp)")
        if "MPI_Gatherv" in code:
            notes.append("Dung MPI_Gatherv (an toan khi H khong chia het cho P)")
        elif "MPI_Gather" in code:
            notes.append("Dung MPI_Gather (can kiem tra truong hop H khong chia het cho P)")
        else:
            notes.append("Khong thay MPI_Gather/MPI_Gatherv")
        if '"-p"' not in code and "'-p'" not in code and "getopt" not in code:
            notes.append("Khong thay phan tich tham so -p")
        g_idx = max(code.find("MPI_Gather"), code.find("MPI_Gatherv"))
        w_idx = code.rfind("MPI_Wtime")
        c_idx = code.rfind("now()")
        t_idx = max(w_idx, c_idx)
        if g_idx != -1 and t_idx != -1 and t_idx < g_idx:
            notes.append("Canh bao do dac: moc ket thuc timer dat TRUOC MPI_Gather")
    if '"-t"' not in code and "'-t'" not in code and "getopt" not in code and variant != "mpi_omp":
        notes.append("Khong thay phan tich tham so -t")
    return notes


def run_reference(gxx, env, threads, repeats):
    """Do moc tham chieu cuc bo (mandel_seq.cpp va mandel_omp.cpp)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        seq_exe = tmp_path / "ref_seq.exe"
        omp_exe = tmp_path / "ref_omp.exe"
        subprocess.run(
            [str(gxx), "-O2", "-std=c++17", "-fopenmp", str(REF_DIR / "mandel_seq.cpp"), "-o", str(seq_exe)],
            env=env, check=True, capture_output=True, text=True,
        )
        subprocess.run(
            [str(gxx), "-O2", "-std=c++17", "-fopenmp", str(REF_DIR / "mandel_omp.cpp"), "-o", str(omp_exe)],
            env=env, check=True, capture_output=True, text=True,
        )
        pat = re.compile(r"time=([\d.]+)")

        def measure(exe, args):
            vals = []
            for _ in range(repeats):
                r = subprocess.run([str(exe)] + args, cwd=tmp_path, env=env, capture_output=True, text=True, check=True)
                m = pat.search(r.stdout)
                vals.append(float(m.group(1)))
            return statistics.mean(vals)

        base_args = ["-w", "1920", "-h", "1080", "-i", "1000"]
        t_seq = measure(seq_exe, base_args)
        omp_times = {}
        for t in threads:
            omp_times[t] = measure(omp_exe, base_args + ["-t", str(t)])
        return {"seq_time": t_seq, "omp_times": omp_times, "config": "1920x1080, 1000 iter"}


def evaluate_variant(variant, src_path, label, flags, gxx, env, has_tbb, model_dir, stage, threads, repeats, timeout):
    res = {
        "variant": variant,
        "label": label,
        "file": src_path.name,
        "status": "MISSING",
        "build_ok": False,
        "warnings": 0,
        "runtime_ok": False,
        "image_ok": False,
        "static_notes": [],
        "times": {},
        "time_source": None,
        "speedup_max": None,
        "flat_line_suspect": None,
        "errors": [],
    }
    if not src_path.exists():
        return res

    code = src_path.read_text(encoding="utf-8", errors="replace")
    res["loc"] = sum(1 for ln in code.splitlines() if ln.strip())
    res["static_notes"] = static_audit(variant, code)

    if variant == "mpi_omp" and shutil.which("mpic++") is None:
        res["status"] = "STATIC_ONLY_NO_MPI"
        return res
    if variant == "par_algo" and not has_tbb:
        res["status"] = "SKIPPED_NO_TBB"
        return res

    build_dir = model_dir / "_build" / stage
    build_dir.mkdir(parents=True, exist_ok=True)
    exe = build_dir / f"{variant}.exe"
    cmd = [str(gxx)] + list(flags) + [str(src_path), "-o", str(exe)]
    if variant == "par_algo" and has_tbb:
        cmd.append("-ltbb")

    comp = subprocess.run(cmd, env=env, capture_output=True, text=True)
    res["compiler_stderr"] = comp.stderr.strip()
    res["warnings"] = len(re.findall(r"\bwarning:", comp.stderr))
    if comp.returncode != 0:
        res["status"] = "BUILD_FAIL"
        res["errors"].append("Loi bien dich (xem compiler_stderr)")
        return res

    res["build_ok"] = True
    preview_saved = False
    all_runs_ok = True

    for t in threads:
        reported_vals, wall_vals = [], []
        for rep in range(repeats):
            with tempfile.TemporaryDirectory() as run_tmp:
                run_dir = Path(run_tmp)
                t0 = time.perf_counter()
                try:
                    p = subprocess.run(
                        [str(exe), "-t", str(t)],
                        cwd=run_dir, env=env, capture_output=True, text=True, timeout=timeout,
                    )
                except subprocess.TimeoutExpired:
                    all_runs_ok = False
                    res["errors"].append(f"Timeout ({timeout}s) tai -t {t}")
                    break
                wall = time.perf_counter() - t0
                if p.returncode != 0:
                    all_runs_ok = False
                    res["errors"].append(f"Crash (exit={p.returncode}) tai -t {t}: {p.stderr.strip()[:160]}")
                    break
                wall_vals.append(wall)
                rep_t = parse_reported_time(p.stdout)
                if rep_t is not None and rep_t > 0:
                    reported_vals.append(rep_t)

                if not preview_saved and rep == 0:
                    imgs = sorted(
                        [f for f in run_dir.iterdir() if f.suffix.lower() in (".pbm", ".pgm", ".ppm")],
                        key=lambda f: f.stat().st_size, reverse=True,
                    )
                    if not imgs:
                        res["image_info"] = {"valid": False, "issue": "Khong tim thay tep .pbm/.pgm/.ppm"}
                    else:
                        preview_path = model_dir / f"preview_{stage}_{variant}.png"
                        info = inspect_netpbm(imgs[0], preview_path)
                        res["image_info"] = info
                        res["image_ok"] = bool(info["valid"])
                    preview_saved = True

        if not all_runs_ok:
            break
        if reported_vals:
            res["times"][t] = statistics.mean(reported_vals)
            res["time_source"] = "stdout"
        elif wall_vals:
            res["times"][t] = statistics.mean(wall_vals)
            res["time_source"] = "wall_fallback"

    res["runtime_ok"] = all_runs_ok and bool(res["times"])
    if res["runtime_ok"] and min(threads) in res["times"] and max(threads) in res["times"]:
        t_min = res["times"][min(threads)]
        t_max = res["times"][max(threads)]
        if t_max > 0:
            sp = t_min / t_max
            res["speedup_max"] = round(sp, 2)
            if max(threads) >= 4:
                res["flat_line_suspect"] = sp < 1.25

    if not res["runtime_ok"]:
        res["status"] = "RUNTIME_FAIL"
    elif not res["image_ok"]:
        res["status"] = "IMAGE_FAIL"
    elif res["flat_line_suspect"]:
        res["status"] = "FLAT_LINE_SUSPECT"
    else:
        res["status"] = "PASS"
    return res


def plot_scaling(results, ref, threads, model_name, stage, out_png):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
    has_curve = False

    # Moc tham chieu OpenMP cuc bo
    if ref and ref["omp_times"]:
        ref_t1 = ref["omp_times"][min(threads)]
        ref_sp = [ref_t1 / ref["omp_times"][t] for t in threads]
        ax1.plot(threads, ref_sp, "k--", linewidth=1.6, label="Tham chieu local (OpenMP)")
        ax2.plot(threads, [ref["omp_times"][t] for t in threads], "k--", linewidth=1.6, label="Tham chieu local (OpenMP)")

    ax1.plot(threads, [t / min(threads) for t in threads], ":", color="gray", label="Tuyen tinh ly tuong")

    for r in results:
        if r["runtime_ok"] and all(t in r["times"] for t in threads):
            has_curve = True
            t1 = r["times"][min(threads)]
            ys = [t1 / r["times"][t] for t in threads]
            ts = [r["times"][t] for t in threads]
            ax1.plot(threads, ys, "o-", label=r["label"])
            ax2.plot(threads, ts, "o-", label=r["label"])

    ax1.set_xlabel("Tham so -t")
    ax1.set_ylabel("Speedup so voi -t 1")
    ax1.set_title(f"{model_name} ({stage}) - Speedup")
    ax1.grid(True, alpha=0.4)
    ax1.legend(fontsize=8)

    ax2.set_xlabel("Tham so -t")
    ax2.set_ylabel("Thoi gian (giay)")
    ax2.set_title(f"{model_name} ({stage}) - Thoi gian chay")
    ax2.grid(True, alpha=0.4)
    ax2.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
    return has_curve


def write_markdown_report(model_name, stage, env_info, results, ref, threads, out_md):
    lines = [
        f"# Kết quả đánh giá bổ sung: `{model_name}` (giai đoạn `{stage}`)",
        "",
        f"- **Thời điểm chạy:** {env_info['timestamp']}",
        f"- **Hệ điều hành / CPU:** {env_info['os']} — {env_info['cpu_threads']} luồng logic",
        f"- **Trình biên dịch:** `{env_info['compiler_version']}`",
        f"- **Hỗ trợ sẵn trên máy:** OpenMP = Có, C++20 coroutines = Có, Intel TBB = {'Có' if env_info['has_tbb'] else 'Không'}, MPI = {'Có' if env_info['has_mpi'] else 'Không'}",
        f"- **Dãy `-t` kiểm thử:** {threads} (lặp {env_info['repeats']} lần lấy trung bình)",
        "",
        "## Tổng hợp theo biến thể",
        "",
        "| Biến thể | Trạng thái | LOC | Biên dịch (cảnh báo) | Thực thi | Ảnh Netpbm | Speedup (-t max/-t 1) | Nghi ngờ bỏ qua -t | Ghi chú |",
        "|---|---|---:|---|---|---|---|---|---|",
    ]
    for r in results:
        b = "✓" if r["build_ok"] else ("—" if r["status"] in ("MISSING", "SKIPPED_NO_TBB", "STATIC_ONLY_NO_MPI") else "×")
        if r["build_ok"]:
            b += f" ({r['warnings']})"
        rt = "✓" if r["runtime_ok"] else ("—" if not r["build_ok"] else "×")
        im_info = r.get("image_info") or {}
        if r["image_ok"]:
            im = f"✓ ({im_info.get('magic','')}, {im_info.get('width','')}×{im_info.get('height','')})"
        elif r["runtime_ok"]:
            im = f"× ({im_info.get('issue','lỗi ảnh')})"
        else:
            im = "—"
        sp = f"{r['speedup_max']:.2f}× ({r['time_source']})" if r["speedup_max"] is not None else "—"
        flat = "Có (đường phẳng)" if r["flat_line_suspect"] else ("Không" if r["flat_line_suspect"] is False else "—")
        notes = "; ".join(r["errors"] + r["static_notes"]) or "—"
        lines.append(
            f"| {r['label']} | `{r['status']}` | {r.get('loc', '—')} | {b} | {rt} | {im} | {sp} | {flat} | {notes} |"
        )

    if ref:
        t_min, t_max = min(threads), max(threads)
        sp_ref = ref["omp_times"][t_min] / ref["omp_times"][t_max]
        lines += [
            "",
            "## Mốc tham chiếu cục bộ (`Demo/mandelbrot/mandel_omp.cpp`, 1920×1080, 1000 vòng)",
            "",
            f"- Tuần tự: `{ref['seq_time']:.4f} s`",
            f"- OpenMP `-t {t_min}`: `{ref['omp_times'][t_min]:.4f} s` → `-t {t_max}`: `{ref['omp_times'][t_max]:.4f} s` (tăng tốc `{sp_ref:.2f}×`)",
        ]

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def init_model(model_name):
    base = EVAL_ROOT / model_name
    (base / "raw").mkdir(parents=True, exist_ok=True)
    (base / "fixed").mkdir(parents=True, exist_ok=True)
    notes = base / "notes.md"
    if not notes.exists():
        notes.write_text(
            f"# Nhật ký đánh giá mô hình `{model_name}`\n\n"
            "- **Ngày sinh mã:** \n"
            "- **Phiên bản / nguồn mô hình:** (vd: Gemini 2.5 Pro web, Claude Sonnet 4.5, GPT-5.2, Qwen3-Coder...)\n"
            "- **Cách sinh:** 1 lần duy nhất cho mỗi biến thể bằng nguyên văn prompt trong `Demo/llm_eval/README.md`.\n\n"
            "## Nhật ký sửa lỗi tối thiểu (`raw/` -> `fixed/`)\n\n"
            "| Biến thể | Lỗi gặp phải | Số dòng sửa | Ghi chú |\n"
            "|---|---|---:|---|\n"
            "| `async.cpp` | | | |\n"
            "| `par_algo.cpp` | | | |\n"
            "| `coroutine.cpp` | | | |\n"
            "| `openmp.cpp` | | | |\n"
            "| `mpi_omp.cpp` | | | |\n",
            encoding="utf-8",
        )
    print(f"Da khoi tao thu muc: {base}")
    print("Dat cac file raw (async.cpp, par_algo.cpp, coroutine.cpp, openmp.cpp, mpi_omp.cpp) vao raw/ roi chay:")
    print(f"  python eval_llm.py {model_name}")


def main():
    ap = argparse.ArgumentParser(description="Danh gia ma C++ Mandelbrot do LLM sinh.")
    ap.add_argument("model", nargs="?", help="Ten thu muc mo hinh trong Demo/llm_eval/")
    ap.add_argument("--init", metavar="MODEL", help="Khoi tao thu muc raw/, fixed/, notes.md cho mo hinh moi")
    ap.add_argument("--stage", choices=("raw", "fixed"), default="raw")
    ap.add_argument("--threads", type=int, nargs="+", default=[1, 2, 4, 8, 12])
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--no-ref", action="store_true", help="Bo qua do moc tham chieu local")
    args = ap.parse_args()

    if args.init:
        init_model(args.init)
        return
    if not args.model:
        ap.error("Can nhap ten mo hinh hoac dung --init <ten_mo_hinh>.")

    model_dir = EVAL_ROOT / args.model
    src_dir = model_dir / args.stage
    if not src_dir.is_dir():
        sys.exit(f"Khong tim thay thu muc {src_dir}. Chay --init {args.model} truoc.")

    gxx, ver, env, has_tbb = find_working_gxx()
    has_mpi = shutil.which("mpic++") is not None
    print(f"Trinh bien dich: {gxx} ({ver})")
    print(f"CPU: {os.cpu_count()} luong | TBB: {has_tbb} | MPI: {has_mpi}\n")

    results = []
    for var, fname, label, flags in VARIANTS:
        r = evaluate_variant(
            var, src_dir / fname, label, flags, gxx, env, has_tbb,
            model_dir, args.stage, args.threads, args.repeats, args.timeout,
        )
        results.append(r)
        print(f"[{r['status']:18s}] {label:26s} | speedup={r['speedup_max']} | img={r['image_ok']}")

    ref = None if args.no_ref else run_reference(gxx, env, args.threads, args.repeats)
    env_info = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "os": f"{platform.system()} {platform.release()}",
        "cpu_threads": os.cpu_count(),
        "compiler": str(gxx),
        "compiler_version": ver,
        "has_tbb": has_tbb,
        "has_mpi": has_mpi,
        "repeats": args.repeats,
    }

    out_json = model_dir / f"results_{args.stage}.json"
    out_md = model_dir / f"report_{args.stage}.md"
    out_png = model_dir / f"scaling_{args.stage}.png"

    out_json.write_text(json.dumps({"env": env_info, "reference": ref, "results": results}, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown_report(args.model, args.stage, env_info, results, ref, args.threads, out_md)
    plot_scaling(results, ref, args.threads, args.model, args.stage, out_png)

    print(f"\nDa xuat:\n  - {out_md}\n  - {out_png}\n  - {out_json}")


if __name__ == "__main__":
    main()
