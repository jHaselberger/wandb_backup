from tqdm import tqdm
import pandas as pd
import wandb
import argparse
import json

parser = argparse.ArgumentParser(description="W&B Backup Tool")
parser.add_argument(
    "entity",
    type=str,
    help="The wandb entity. Most times this is simply your username.",
)
parser.add_argument("project", type=str, help="The name of the project to backup")
parser.add_argument(
    "backup_root", type=str, help="The root dir, where all the files are stored."
)
parser.add_argument(
    "--skip_media",
    help="Skip all media files",
    default=False,
    action="store_true",
)
parser.add_argument(
    "--skip_images",
    help="Skip all images",
    default=False,
    action="store_true",
)
parser.add_argument(
    "--timeout",
    help="Timeout for wandb fetch in seconds",
    type=int,
    default=30,
)
args = parser.parse_args()

entity = args.entity
project = args.project
backup_root = args.backup_root
skip_media = args.skip_media
skip_images = args.skip_images

# init the API
api = wandb.Api(timeout=args.timeout)

# get all the runs of the project
runs = api.runs(f"{entity}/{project}")
print(f"{len(runs)} runs of {entity}/{project} will be backuped at {backup_root}")

for _r in tqdm(runs, position=0, desc="Processed runs"):

    # get all the files of each run
    for file in tqdm(
        _r.files(),
        position=1,
        leave=False,
        desc=f"Downloaded files of {_r.name}",
        colour="#bdc3c7",
    ):
        if (skip_media and "media" in str(file)) or (
            skip_images and "images" in str(file)
        ):
            pass
        else:
            file.download(
                root=f"{backup_root}/{entity}/{project}/{_r.name}", replace=True
            )

    # store the config
    with open(
        f"{backup_root}/{entity}/{project}/{_r.name}/run_config.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(_r.config, f, ensure_ascii=False, indent=4)

    # store the history
    _r.history().to_json(f"{backup_root}/{entity}/{project}/{_r.name}/run_history.json")

print("Finished!")
