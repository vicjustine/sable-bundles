import csv
import hashlib
import io

import json
import os
from pathlib import Path
from zipfile import ZipFile

def inspect(path): 
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with ZipFile(path) as bundle: 
        if bundle.namelist() != ["catalog.csv", "manifest.json"]: 
            raise ValueError("Unexpected ZIP members")
        manifest = json.loads(bundle.read("manifest.json"))
        catalog = io.StringIO(bundle.read("catalog.csv").decode("utf-8"))
        rows = list(csv.DictReader(catalog))
        facts = {
            "items": len(rows),
            "total_cents": sum(int(row["price_cents"]) for row in rows),
        }
        if facts != manifest:
            raise ValueError("Manifest disagrees with the catalog")
        first = bundle.getinfo("catalog.csv").date_time
    return digest, facts, first

def verify ():
    left, right = (inspect(Path(f"{side}/catalog.zip")) for side in ("left", "right"))
    same = left[0] == right [0]
    status = "REPRODUCIBLE" if same else "BYTE MISMATCH"
    lines = [
        f"## {status}", 
        "",
        "|  Build  |  SHA-256  |  Items  | Cents | ZIP year |", 
        "|  --- |  ---  |  ---:  | ---:  | ---:  |",
    ]
    for side, (digest, facts, stamp) in zip (("left", "right"), (left, right)):
        items, cents = facts["items"], facts["total_cents"]
        lines.append(f"| {side} |  `{digest}` | {items} | {cents} | {stamp[0]} |")
    report = "\n".join(lines) + "\n"
    print(report)
    Path("comparison.md").write_text(report, encoding="utf-8")
    if summary := os.getenv("GITHUB_STEP_SUMMARY"): 
        with open(summary, "a", encoding = "utf-8") as handle:
            handle.write(report)
    return 0 if same else 1

if __name__ == "__main__":
    raise SystemExit(verify())
















  
