#!/usr/bin/env python3
# ==========================================
# FILE CHAOS GENERATOR (L10++ STYLE)
# ==========================================

import os
import sys
import random
import string
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock

# ================= UTF-8 SAFE =================
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="ignore")

# ================= GLOBAL LOCK =================
print_lock = Lock()
counter_lock = Lock()
files_created = 0

# ================= EXTENSIONS =================
BASE_EXTENSIONS = [
    ".jpg",
    ".png",
    ".docx",
    ".pdf",
    ".txt",
    ".zip",
    ".java",
    ".c",
    ".cpp",
    ".xlsx",
    ".pptx",
    ".mp3",
    ".mp4",
    ".html",
    ".css",
    ".js",
]


def generate_extensions(n):
    exts = BASE_EXTENSIONS.copy()
    while len(exts) < n:
        ext = "".join(random.choices(string.ascii_lowercase, k=3))
        if ext not in exts:
            exts.append(ext)
    return exts[:n]


# ================= RANDOM HELPERS =================
def random_filename(ext_list):
    name = "".join(random.choices(string.ascii_letters + string.digits, k=12))
    ext = random.choice(ext_list)
    return f"{name}.{ext}"


def random_bytes(size):
    return os.urandom(size)


def random_subdir(base, depth, width):
    path = Path(base)
    for _ in range(depth):
        folder = "".join(random.choices(string.ascii_lowercase, k=5))
        path = path / folder
        if random.random() < width:
            path.mkdir(parents=True, exist_ok=True)
    return path


# ================= FILE CREATION =================
def create_file(base_dir, ext_list, min_size, max_size, use_tree):
    global files_created

    try:
        if use_tree:
            directory = random_subdir(base_dir, depth=3, width=0.7)
        else:
            directory = Path(base_dir)

        filename = random_filename(ext_list)
        filepath = directory / filename

        size = random.randint(min_size, max_size)

        with open(filepath, "wb") as f:
            f.write(random_bytes(size))

        with counter_lock:
            files_created += 1

    except Exception as e:
        with print_lock:
            print(f"[ERROR] {e}")


# ================= WORKER =================
def worker(batch_size, base_dir, ext_list, min_size, max_size, use_tree):
    for _ in range(batch_size):
        create_file(base_dir, ext_list, min_size, max_size, use_tree)


# ================= PROGRESS =================
def progress_monitor(total):
    import time

    while True:
        with counter_lock:
            done = files_created

        percent = (done / total) * 100
        with print_lock:
            print(f"\r[PROGRESS] {done}/{total} ({percent:.2f}%)", end="")

        if done >= total:
            break
        time.sleep(0.5)

    print("\n[OK] Done.")


# ================= MAIN =================
def main():
    parser = argparse.ArgumentParser(description="File Chaos Generator")

    # parser.add_argument("--dir", default="./random_files", help="Output directory")
    parser.add_argument("--dir", default="./dist/testing/", help="Output directory")
    parser.add_argument("--files", type=int, default=25, help="Total files")
    parser.add_argument("--ext", type=int, default=3, help="Total extensions")
    parser.add_argument("--threads", type=int, default=8, help="Threads")
    parser.add_argument("--min", type=int, default=1024, help="Min file size (bytes)")
    parser.add_argument(
        "--max", type=int, default=1024 * 50, help="Max file size (bytes)"
    )
    parser.add_argument(
        "--tree", action="store_true", help="Enable directory tree mode"
    )

    args = parser.parse_args()

    base_dir = Path(args.dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    ext_list = generate_extensions(args.ext)

    files_per_thread = args.files // args.threads
    remainder = args.files % args.threads

    tasks = [files_per_thread] * args.threads
    for i in range(remainder):
        tasks[i] += 1

    print("[INFO] Starting generation...")
    print(f"[INFO] Directory: {base_dir}")
    print(
        f"[INFO] Files: {args.files}, Extensions: {args.ext}, Threads: {args.threads}"
    )

    # Start progress monitor
    from threading import Thread

    monitor_thread = Thread(target=progress_monitor, args=(args.files,), daemon=True)
    monitor_thread.start()

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for batch in tasks:
            executor.submit(
                worker, batch, base_dir, ext_list, args.min, args.max, args.tree
            )

    monitor_thread.join()

    print(f"[OK] Created {args.files} files in '{base_dir}'")


# ================= ENTRY =================
if __name__ == "__main__":
    main()
