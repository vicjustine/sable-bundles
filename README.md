# Sable Bundles

A synthetic catalog for offline distribution. Each row identifies an item,
its department and its replacement price in cents. The two source sets
represent independently collected snapshots of the same catalog.

The package acceptance contract is identical ZIP bytes from both snapshots,
regardless of row order and source timestamps. A verified bundle must
contain catalog.csv and manifest.json.
