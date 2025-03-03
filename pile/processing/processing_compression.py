import argparse
from functools import partial
from pathlib import Path
from pprint import pprint

import numpy as np
from datasets import disable_caching, load_from_disk
from squeakily.core import Pipeline
from squeakily.filter import check_compression_ratio

disable_caching()


# Parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "--data_dir",
    type=str,
    required=True,
    help="The directory where the data is stored.",
)
parser.add_argument(
    "--min_percentile",
    type=float,
    default=0.01,
    help="The minimum percentile to use for the threshold.",
)
parser.add_argument(
    "--max_percentile",
    type=float,
    default=0.99,
    help="The maximum percentile to use for the threshold.",
)
parser.add_argument(
    "--output_dir",
    type=str,
    required=True,
    help="The directory where the output should be stored.",
)
args = parser.parse_args()

# create the output directory if it does not exist
output_dir = Path(args.output_dir)
output_dir.mkdir(parents=True, exist_ok=True)

# Get all the files in the data directory
data_dir = Path(args.data_dir)
ignored_datasets = [
    "AMPS",
    "DMMath",
    "Enwiki",
    "EuroParliamentProceedings",
    "Gutenberg",
    "OtherWiki",
    "TheStack",
    "GithubDiffs",
]
dataset_cats = [
    x.name for x in data_dir.iterdir() if x.is_dir() and x.name not in ignored_datasets
][:2]

tmp_ds = [
    {
        "dataset": load_from_disk(data_dir / k).select(range(1_000)),
        "name": k,
        "columns": ["text"],
        "filters": [check_compression_ratio],
        "cleaners": [],
    }
    for k in dataset_cats
]
datasources = []
for idx, ds in enumerate(tmp_ds):
    pipeline = Pipeline([ds])
    pipeline.run(dry_run=True)
    compression_ratios = pipeline.datasources[0]["dataset"][
        "check_compression_ratio_criteria"
    ]
    min_compression_ratio = np.quantile(compression_ratios, args.min_percentile)
    check_compression_ratio_p = partial(
        check_compression_ratio, compression_threshold=min_compression_ratio
    )
    check_compression_ratio_p.__name__ = "check_compression_ratio"
    ds["filters"] = [check_compression_ratio_p]

    datasources.append(ds)

pprint(datasources)

pipeline = Pipeline(datasources)
pipeline.run()

pprint(pipeline.datasources)

# Save the resulting datasets
for name, ds in zip(dataset_cats, pipeline.datasources):
    ds["dataset"].save_to_disk(output_dir / name)
