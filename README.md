# W&B Backup
Tiny python tool to backup all wandb files.

## Usage
```sh
usage: wandb_backup.py [-h] [--skip_media] [--skip_images] [--timeout TIMEOUT] [--threads THREADS] [--run_ids [RUN_IDS [RUN_IDS ...]]] entity project backup_root

W&B Backup Tool

positional arguments:
  entity                The wandb entity. Most times this is simply your username.
  project               The name of the project to backup
  backup_root           The root dir, where all the files are stored.

optional arguments:
  -h, --help            show this help message and exit
  --skip_media          Skip all media files
  --skip_images         Skip all images
  --timeout TIMEOUT     Timeout for wandb fetch in seconds
  --threads THREADS     Number of download threads. According to the documentation wandb allows only 200 requests per minute.
  --run_ids [RUN_IDS [RUN_IDS ...]]
                        only download runs with given ids
```

`--skip_images --threads 10 --timeout 120` worked without errors. 20 threads with 30s timeout resulted in timeouts. 