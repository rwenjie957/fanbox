import requests
import json
from pathlib import Path
import concurrent.futures
from tqdm import tqdm


def make_path(path):
    _path = Path(path)
    if not _path.is_dir():
        Path.mkdir(_path)
    return _path

def download(cookie, post_id):
    url = 'https://api.fanbox.cc/post.info'
    headers = {
        'authority': 'api.fanbox.cc',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': cookie,
        'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
        'Origin': 'https://www.fanbox.cc',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
        'Sec-Ch-Ua-Platform': "Windows"
    }
    payload = {'postId': post_id}
    r = requests.get(url, headers=headers, params=payload)
    r.encoding = 'utf-8'
    data = json.loads(r.text)
    return data


def analysis(post):
    _prev, _next = '', ''
    if isinstance(post['body']['prevPost'], dict):
        _prev = post['body']['prevPost']['id']
    if isinstance(post['body']['nextPost'], dict):
        _next = post['body']['nextPost']['id']

    images = {}
    if body := post['body']['body']:
        if image_map := body.get('imageMap', None):
            for v in image_map.values():
                name = '.'.join((v['id'], v['extension']))
                images[name] = v['originalUrl']
        elif image_map := body.get('images', None):
            for v in image_map:
                name = '.'.join((v['id'], v['extension']))
                images[name] = v['originalUrl']
        else:
            print('该文章没有图片')

    else:
        print('文章可能未解锁或者不可访问')
    return _prev, _next, images


class DownloadPicture:
    def __init__(self, save_path, post_id, cookies, urls, log):    # log: {'status':'locked','pictures':{}}
        self.log=log
        self.urls = urls
        self.post_id = post_id
        self.save_path = Path(save_path)
        self.log['pictures'] = self.log.get('pictures', {})
        self.s = requests.session()
        self.s.headers.update(
            {
            'authority': 'api.fanbox.cc',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cookie': cookies,
            'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
            'Origin': 'https://www.fanbox.cc',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
            'Sec-Ch-Ua-Platform': "Windows"
            }
        )

    def _download(self, filename, url):
        with open(self.save_path / self.post_id / filename, 'wb') as file:
            pic = self.s.get(url, stream=True)
            for chunk in tqdm(pic.iter_content(), desc=f'{filename}'):
                file.write(chunk)
        self.log['pictures'][filename] = True
        # print(f'{filename}下载成功')

    def single_download(self):
        for name, url in self.urls.items():
            self._download(name, url)

    def multi_download(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as con:
            for name, url in self.urls.items():
                try:
                    if not self.log['pictures'].get(name, False):
                        con.submit(self._download, name, url)
                except Exception as e:
                    print(e)


if __name__ == '__main__':

    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    cookies = config['cookies']

    # dat = download(cookies, 8789178)
    # with open('3.json', 'w', encoding='utf-8') as f2:
    #     json.dump(dat, f2, ensure_ascii=False, indent=4)
    #
    with open('1.json', 'r', encoding='utf-8') as f3:
        dat2 = json.load(f3)
    p, n,i = analysis(dat2)
    print(i)
    logs = {}
    d = DownloadPicture('8722935',cookies, i, logs)
    print(d.log)

    # with open('log.json', 'r', encoding='utf-8') as file:
        # t = json.load(file)
    # print(t['チノマロン']['post_id']['8722935']['pictures']['name1'])