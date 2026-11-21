"""Resumable, MD5-verified downloader for the DerStandard dataset (doi:10.82201/RVQGUG).

Usage:
    python download.py <dest_dir> [--include-embeddings] [--workers N]

- Reads files_metadata.json (Dataverse file listing saved next to this script).
- Downloads tabular files in their ORIGINAL format (.tsv), whose MD5 is the one listed.
- Resumes partial files via HTTP Range, retries forever with backoff, verifies size + MD5.
- Already-verified files are recorded in <dest_dir>/.verified and skipped on rerun.
"""
import hashlib, json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://dataverse.bsc.es/api/access/datafile/{id}"
LOG = os.path.join(HERE, "download.log")


def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def plan(dest, include_embeddings):
    files = json.load(open(os.path.join(HERE, "files_metadata.json"), encoding="utf-8"))["data"]
    out = []
    for f in files:
        df = f["dataFile"]
        folder = f.get("directoryLabel", "")
        if folder == "embeddings" and not include_embeddings:
            continue
        tab = df.get("tabularData", False)
        name = df.get("originalFileName") if tab else df["filename"]
        size = df.get("originalFileSize") if tab else df["filesize"]
        url = BASE.format(id=df["id"]) + ("?format=original" if tab else "")
        out.append(dict(id=df["id"], url=url, size=size, md5=df["checksum"]["value"],
                        path=os.path.join(dest, folder, name), rel=f"{folder}/{name}"))
    return out


def fetch(item, verified_path):
    path, size = item["path"], item["size"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    part = path + ".part"
    attempt = 0
    while True:
        attempt += 1
        try:
            have = os.path.getsize(part) if os.path.exists(part) else 0
            if have < size:
                req = urllib.request.Request(item["url"])
                if have:
                    req.add_header("Range", f"bytes={have}-")
                with urllib.request.urlopen(req, timeout=120) as r:
                    mode = "ab" if (have and r.status == 206) else "wb"
                    with open(part, mode) as f:
                        while True:
                            buf = r.read(1 << 20)
                            if not buf:
                                break
                            f.write(buf)
            got = os.path.getsize(part)
            if got != size:
                raise IOError(f"size mismatch {got} != {size}")
            if md5_of(part) != item["md5"]:
                os.remove(part)
                raise IOError("md5 mismatch, restarting file from scratch")
            os.replace(part, path)
            with open(verified_path, "a", encoding="utf-8") as f:
                f.write(item["rel"] + "\n")
            return item
        except Exception as e:
            wait = min(300, 5 * 2 ** min(attempt, 6))
            log(f"RETRY {item['rel']} attempt {attempt}: {e!r}; sleeping {wait}s")
            time.sleep(wait)


def main():
    dest = sys.argv[1]
    include_emb = "--include-embeddings" in sys.argv
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 4
    os.makedirs(dest, exist_ok=True)
    verified_path = os.path.join(dest, ".verified")
    done = set(open(verified_path, encoding="utf-8").read().split()) if os.path.exists(verified_path) else set()
    items = [i for i in plan(dest, include_emb) if i["rel"] not in done]
    total = sum(i["size"] for i in items)
    log(f"START {len(items)} files, {total/1e9:.2f} GB pending (embeddings={include_emb}, workers={workers})")
    t0, acc = time.time(), 0
    with ThreadPoolExecutor(workers) as ex:
        for fut in as_completed([ex.submit(fetch, i, verified_path) for i in items]):
            it = fut.result()
            acc += it["size"]
            el = time.time() - t0
            log(f"OK {it['rel']} | {acc/1e9:.2f}/{total/1e9:.2f} GB | {acc/1e6/el:.1f} MB/s")
    log("DONE all files verified")


if __name__ == "__main__":
    main()
