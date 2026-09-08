#!/usr/bin/env python3
"""Generate a review batch of exact NNTT spatial-coverage candidates."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from rdflib import Dataset, Graph, Namespace, URIRef


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "build" / "sandbox" / "reports"
RDF_DIR = ROOT / "build" / "sandbox" / "rdf"
DEFAULT_FEATURES_DIR = (
    ROOT.parent / "indigenous-data-catalogue/resources/reference/datasets/features"
)

SDO = Namespace("https://schema.org/")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features-dir", type=Path, default=DEFAULT_FEATURES_DIR)
    parser.add_argument("--limit", type=int, default=25)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidate_path = REPORT_DIR / "odrl-spatial-target-candidates.csv"
    if not candidate_path.exists():
        raise FileNotFoundError(
            "Run the spatial candidate audit before generating a review batch"
        )

    with candidate_path.open(encoding="utf-8", newline="") as source:
        exact_rows = [
            row
            for row in csv.DictReader(source)
            if row["confidence"] == "high"
            and row["match_method"] == "nntt-file-number"
        ]
    # The audit is already sorted by confidence and agreement name. Deduplicate
    # the exact Agreement-feature pair defensively before selecting the batch.
    seen: set[tuple[str, str]] = set()
    selected: list[dict[str, str]] = []
    for row in exact_rows:
        key = (row["agreement"], row["candidate_feature"])
        if key in seen:
            continue
        seen.add(key)
        selected.append(row)
        if args.limit and len(selected) >= args.limit:
            break

    features = Dataset(default_union=True)
    for path in sorted(args.features_dir.resolve().glob("nntt-ilua-*.trig")):
        features.parse(path, format="trig")

    output = Graph()
    output.bind("sdo", SDO)
    missing: list[str] = []
    for row in selected:
        agreement = URIRef(row["agreement"])
        feature = URIRef(row["candidate_feature"])
        output.add((agreement, SDO.spatialCoverage, feature))
        names = list(features.objects(feature, SDO.name))
        if not names:
            missing.append(str(feature))
            continue
        for name in names:
            output.add((feature, SDO.name, name))

    if missing:
        raise RuntimeError("Missing feature data: " + ", ".join(missing))

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    RDF_DIR.mkdir(parents=True, exist_ok=True)
    ttl_path = REPORT_DIR / "spatial-coverage-review.ttl"
    loaded_path = RDF_DIR / "spatial-coverage-review.ttl"
    header = (
        "# PROVISIONAL REVIEW DATA: exact NNTT identifier matches.\n"
        "# These spatialCoverage assertions are loaded locally for sanity checking only.\n\n"
    )
    turtle = header + output.serialize(format="longturtle")
    ttl_path.write_text(turtle, encoding="utf-8")
    loaded_path.write_text(turtle, encoding="utf-8")

    csv_path = REPORT_DIR / "spatial-coverage-review.csv"
    fields = list(selected[0]) + ["review_decision", "review_notes"]
    with csv_path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        for row in selected:
            writer.writerow({**row, "review_decision": "", "review_notes": ""})

    Graph().parse(ttl_path, format="turtle")
    print(
        f"Wrote {len(selected)} provisional spatialCoverage assertions and their "
        f"NNTT feature names to {ttl_path.relative_to(ROOT)}"
    )
    print(f"Loaded review graph at {loaded_path.relative_to(ROOT)}")
    print(f"Wrote {csv_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
