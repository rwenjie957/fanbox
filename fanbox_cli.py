from fanbox import *
from utils import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', type=str, default='config.json', help='config file')
parser.add_argument('-m', '--mode', type=str, default='single', choices=['multiple', 'single'], help='whether use multiple threading to download')
parser.add_argument('-f', '--fix', action='store_true', help='re-download the files that fails to download')
parser.add_argument('-t', '--threading', type=int, default=5, help='use how many threads to download')
parser.add_argument('-p', '--proxy', action='store_true', help='whether use proxy')
parser.add_argument('-r', '--re-download', nargs='+', help='re-download the specific post')
args = parser.parse_args()

print(args)

allow_proxy = False
config_file = Path(args.config)
if args.proxy:
    allow_proxy=True
f = Fanbox(config_file, args.threading, allow_proxy)
if args.fix:
    f.fix()
elif args.re_download:
    for i in args.re_download:
        f.re_download(i)
else:
    f.update(args.mode)

