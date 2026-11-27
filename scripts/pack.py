import argparse
import csv
import io
import json
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo

HEADER = ["sku", "department", "price_cents"]
EPOCH = (2020, 1, 1, 0, 0, 0)

def read_catalog(source):
    with source.open(encoding="utf-8", newline="") as handle: 
        reader = csv.DictReader(handle)
        if reader.fieldnames != HEADER:
            raise ValueError("Unexpected catalog header")
        rows = list(reader)

    seen = set()
    catalog = []
    for row in rows: 
        sku = row["sku"].strip()
        department = row["department"].strip()
        price = int(row["price_cents"])
        if not sku or not department or sku in seen or price <= 0:
            raise ValueError(f"Invalid or duplicate SKU: {sku}")
        seen.add(sku)
        catalog.append((sku, department, price))
    return sorted(catalog)

def package(source, target, drift): 
    rows = read_catalog(source)
    csv_text = io.StringIO(newline="")
    writer = csv.writer(csv_text, lineterminator="\n")
    writer.writerow(HEADER)
    writer.writerows(rows)
    manifest = {
      "items": len(rows),
      "total_cents": sum(row[2] for row in rows),
    }
    contents = {
        "catalog.csv": csv_text.getvalue(),
        "manifest.json": json.dumps(manifest, sort_keys=True) + "\n",
    }
    stamp = (2021, 1, 1, 0, 0, 0) if drift else EPOCH
    target.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(target, "w") as bundle: 
        for name, payload in sorted(contents.items()):
            member = ZipInfo(name, stamp)
            member.create_system = 3
            member.external_attr = 0o100644 << 16
            member.compress_type = ZIP_STORED
            bundle.writestr(member, payload.encode("utf-8"))

    print(f"Packed {manifest['items']} items / {manifest['total_cents']} cents")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--drift", action="store_true")
    args = parser.parse_args()
    package(args.source, args.target, args.drift)
