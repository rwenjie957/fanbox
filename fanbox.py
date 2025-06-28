from utils import *
from pathlib import Path
import json
import httpx
import concurrent.futures
from tqdm import tqdm
import ssl


class Fanbox:
    def __init__(self, config_file, max_threads=5, allow_proxy=False):
        self.config_file = config_file
        with open(config_file, 'r', encoding='utf-8') as file:
            self.config = json.load(file)

        # 请求头必需的三个参数
        header = {
            'Cookie': self.config['cookie'],
            'Origin': 'https://www.fanbox.cc',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15'
        }

        # 代理
        proxy = None
        if allow_proxy:
            proxy = self.config['proxy']

        # 自定义 TLS 配置 (模拟浏览器的指纹)
        CIPHERS = ':'.join(self.config['CIPHERS'])
        context = ssl.create_default_context()
        context.set_ciphers(CIPHERS)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_3
        context.post_handshake_auth = True  # 部分扩展模拟

        self.client = httpx.Client(headers=header, proxies=proxy, verify=context)

        self.creator = self.config['creator']
        self.post_id = str(self.config['latest_post'])
        self.max_threads = max_threads
        self.save_path = make_path(Path(self.config['save_dir']) / self.creator)
        self.log_file = self.save_path / 'log.json'
        self.url = 'https://api.fanbox.cc/post.info'

        # 加载日志文件
        if not self.log_file.exists():
            Path.touch(self.log_file)
            self.log = {}
            with open(self.log_file, 'w', encoding='utf-8') as logfile:
                json.dump(self.log, logfile)
        else:
            with open(self.log_file, 'r', encoding='utf-8') as logfile:
                self.log = json.load(logfile)


    def download_file(self, filename, url, post_id):
        bar_format = "{desc}: {percentage:3.0f}%|{bar}|{n_fmt}{unit}/{total_fmt}{unit}  [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
        with open(self.save_path / post_id / filename, 'wb') as file:
            with self.client.stream("GET", url) as pic:
                length = int(pic.headers.get('Content-Length', 0))          # 有时服务器返回的响应头没有Content-length字段
                with tqdm(desc=f'{filename}', total=length, unit='B', bar_format=bar_format, unit_scale=True) as pbar:
                        for chunk in pic.iter_bytes(1024):
                            file.write(chunk)
                            pbar.update(len(chunk))
        self.log[post_id]['files'][filename] = True


    def single_download(self, files, post_id):
        for filename, url in files.items():
            self.download_file(filename, url, post_id)

    def multi_download(self, files, post_id):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as con:
            for filename, url in files.items():
                if self.log[post_id]['files'].get(filename):
                    pass
                else:
                    con.submit(self.download_file, filename, url, post_id)

    # 更新post
    def update(self, mode = 'single'):
        post_id = self.post_id                              # 给局部变量赋值类变量的post_id,由于向前搜索，不影响类中原本post_id
        self.log[post_id] = {}
        post_ = self.client.get(self.url, params={'postId':post_id})
        post_data = post_.json()
        _prev, _next, files = analysis(post_data)          # 获取当前文章的所有图片链接和前后文章id
        if not _next:
            print('已是最新')
            return
        try:
            while post_id:
                post_id_directory = make_path(self.save_path / post_id)
                with open(post_id_directory / f'{post_id}.json', 'w', encoding='utf-8') as done:
                    json.dump(post_data, done, indent=4, ensure_ascii=False)

                self.log[post_id]['files'] = {}

                # 下载所有文件
                if files:
                    self.log[post_id]['status'] = 'unlocked'
                    if mode == 'multiple':
                        self.multi_download(files, post_id)
                    else:
                        self.single_download(files, post_id)
                    print(f"{post_id}已下载完毕")
                else:
                    self.log[post_id]['status'] = 'locked'

                if not _next:
                    break
                else:
                    response = self.client.get(self.url, params={'postId':_next})
                    if response.status_code != 200:
                        raise httpx.NetworkError
                    post_id = _next
                    self.log[post_id] = {}
                    post_data = response.json()
                    _prev, _next, files = analysis(post_data)

        except Exception as e:
            print(e)

        finally:
            with open(self.log_file, 'w', encoding='utf-8') as _log:
                json.dump(self.log, _log, ensure_ascii=False, indent=4)
            self.config['latest_post'] = post_id
            with open(self.config_file, 'w', encoding='utf-8') as file:
                json.dump(self.config, file, ensure_ascii=False, indent=4)

    # 修复下载失败的文件
    def fix(self):
        try:
            for post in self.save_path.iterdir():
                if post.is_dir():
                    post_id = post.stem
                    post_log = post / (post_id + '.json')
                    with open(post_log, 'r', encoding='utf-8') as file:
                        _log = json.load(file)
                    _, _, files = analysis(_log)
                    for file in files.keys():
                        if file in self.log[post_id]['files']:
                            pass
                        else:
                            print(f'{post_id}, {file}异常，重新下载')
                            self.download_file(file, files[file], post_id)
        except Exception as e:
            print(e)
        finally:
            with open(self.log_file, 'w', encoding='utf-8') as _log:
                json.dump(self.log, _log, ensure_ascii=False, indent=4)

    # 重新下载指定的post
    def re_download(self, post_id):
        post_id = str(post_id)
        self.log[post_id] = {}
        post_data = self.client.get(self.url, params={'postId': post_id}).json()
        _prev, _next, files = analysis(post_data)
        post_id_directory = make_path(self.save_path / post_id)
        with open(post_id_directory / f'{post_id}.json', 'w', encoding='utf-8') as done:
            json.dump(post_data, done, indent=4, ensure_ascii=False)
        self.log[post_id]['files'] = {}
        if files:
            self.log[post_id]['status'] = 'unlocked'
            self.single_download(files, post_id)
            print(f"{post_id}已下载完毕")
        else:
            self.log[post_id]['status'] = 'locked'

        with open(self.log_file, 'w', encoding='utf-8') as _log:
            json.dump(self.log, _log, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    cfg_file = Path('config.json')
    f = Fanbox(cfg_file, allow_proxy=True)
    f.update()