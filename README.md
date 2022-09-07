# W&B Backup
Tiny python tool to backup all wandb files.

## Usage
```sh
usage: wandbBackupTool.py [-h] [--skip_media] [--skip_images] [--timeout TIMEOUT] entity project backup_root

positional arguments:
  entity             The wandb entity. Most times this is simply your username.
  project            The name of the project to backup
  backup_root        The root dir, where all the files are stored.

  optional arguments:
    -h, --help         show this help message and exit
    --skip_media       Skip all media files
    --skip_images      Skip all images
    --timeout TIMEOUT  Timeout for wandb fetch in seconds
```
