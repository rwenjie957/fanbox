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

# 注意事项
之前使用request库，然后由于JA3指纹被反爬了，后来换成httpx后解决了。最近发现原生httpx也被反爬了，研究了很久之后发现了通过更改TLS加密算法可以反反爬，示例文件已使用safari浏览器的指纹，目前测试可以正常使用
