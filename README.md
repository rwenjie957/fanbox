# fanbox
a simple crawler which can donwload pictures or files in fanbox

# usage
## command line
python3 fanbox_cli.py

- -c --config [config_file]

choose config file, default 'config.json'

- -m --mode

whether use multiple threading to download, default='single', choices=['multiple', 'single']

- -f --fix

re-download the files that fails to download

- -t --threading

use how many threads to download, default=5

- -p --proxy

whether use proxy, default = False
