from fanbox import *
from utils import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', type=str, default='config.json', help='config file')
parser.add_argument('-r', '--reverse', action="store_true", help='whether update the posts recorded before')
parser.add_argument('-s', '--save-path', type=str, default='creator', help='where to save the pictures')
parser.add_argument('-l', '--log-file', type=str, default='log.json', help='choose the log file')
parser.add_argument('-m', '--mode', type=str, default='multiple', choices=['multiple', 'single'], help='whether use multiple threading to download')
args = parser.parse_args()

print(args)

# 加载配置文件
config_file = Path(args.config)
with open(config_file, 'r', encoding='utf-8') as configfile:
    config = json.load(configfile)
creator = config['creator']

# 保存的根目录，默认为./creator
save_root = make_path(args.save_path)
save_path = make_path(save_root / creator)

# 加载日志文件
log_file = save_path / args.log_file

# 加载下载模式
mode = args.mode


f = Fanbox(config, log_file, save_path)
if args.reverse:    # 如果使用-r 参数，则向前搜索文章
    f.prev_search(mode)
else:
    f.next_search(mode)