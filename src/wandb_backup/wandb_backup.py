from requests import ReadTimeout
from tqdm import tqdm
from pathlib import Path
from multiprocessing.pool import ThreadPool as Pool
import multiprocessing
import time
import wandb
import argparse
import json


class Counter(object):
    """
    A counter variable that can be incremented by multiple processes
    """

    def __init__(self):
        self.val = multiprocessing.Value('i', 0)

    def increment(self, n=1):
        with self.val.get_lock():
            self.val.value += n

    @property
    def value(self):
        return self.val.value


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
parser.add_argument(
    "--threads",
    help="Number of download threads. According to the documentation wandb allows only 200 requests per minute.",
    type=int,
    default=10,
)
parser.add_argument(
    "--run_ids",
    help="only download runs with given ids",
    type=str,
    nargs='*',
)
args = parser.parse_args()

entity = args.entity
project = args.project
backup_root = args.backup_root
skip_media = args.skip_media
skip_images = args.skip_images

# create output dir
output_dir_name = f"{backup_root}/{entity}/{project}"
Path(f"{output_dir_name}/").mkdir(parents=True)

# init the API
api = wandb.Api(timeout=args.timeout)

# get all the runs of the project
if args.run_ids is not None:
    run_ids = args.run_ids
else:
    print("Getting list of run ids. This might take a minute.")
    run_ids = [r.id for r in api.runs(f"{entity}/{project}")]
print(f"{len(run_ids)} runs of {entity}/{project} will be backuped at {backup_root}")

# counter for finished downloads
done_counter = Counter()


def process_run(run_id):
    try:
        # can't pass runs directly to thread -> causing recursion crashed
        # passing ids and creating new run objects inside thread is working
        run = api.run(f"{entity}/{project}/{run_id}")

        # create project directory to prevent crash in case there is only a
        # "run_config" and no further files (had this problem with a mysterious sweep)
        download_path = f"{output_dir_name}/{run.name}_(wandb_id_{run.id})"
        Path(download_path).mkdir(parents=True, exist_ok=True)

        # get all the files of each run
        for file in run.files():
            if (skip_media and "media" in str(file)) or (
                    skip_images and "images" in str(file)
            ):
                pass
            else:
                file.download(
                    root=download_path, replace=True
                )

        # store the config
        with open(
                f"{download_path}/run_config.json",
                "w",
                encoding="utf-8",
        ) as f:
            json.dump(run.config, f, ensure_ascii=False, indent=4)

        # store the history
        run.history().to_json(f"{download_path}/run_history.json")
    except ReadTimeout:
        print(f"Read timeout during download of id {run_id}")
    except:
        print(f"Exception happened during download of id {run_id}")
    done_counter.increment()


with Pool(args.threads) as p:
    future = p.map_async(func=process_run, iterable=run_ids)

    # show progress bar
    pbar = tqdm(desc="Processed runs", total=len(run_ids))
    downloads_done = 0
    prev_done = 0
    while not future.ready():
        downloads_done = done_counter.value
        pbar.update(downloads_done - prev_done)
        prev_done = downloads_done
        time.sleep(1)
    pbar.update(done_counter.value - prev_done)
    pbar.close()

    future.wait()

print("Finished!")
