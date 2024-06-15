import os
import shutil
import requests
from pathlib import Path
import json
from tqdm import tqdm


def init(creator):
    if not Path(creator).exists():
        os.mkdir(creator)
        if not (pth := (Path(creator) / 'latest_post.txt')).exists():
            Path.touch(pth)
            exit(0)
# 下载
def download(post_id):                      # 下载网页的文本内容
    url = 'https://api.fanbox.cc/post.info'
    headers = {'authority': 'api.fanbox.cc',
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


def analysis(data):
    pictures = {}
    body = data['body']['body']

    if isinstance(data['body']['nextPost'], dict):
        next_id = data['body']['nextPost']['id']
    else:
        next_id = 0

    if isinstance(body, dict):
        if 'imageMap' in body:
            for k, v in body['imageMap'].items():
                pictures['.'.join([v['id'], v['extension']])] = v['originalUrl']
        elif 'images' in body:
            for pic in body['images']:
                pictures['.'.join([pic['id'], pic['extension']])] = pic['originalUrl']
        elif 'files' in body:
            for file in body['files']:
                pictures['.'.join([file['id'], file['extension']])] = file['url']

    else:
        print('内容未解锁')
    return pictures, next_id


def download_picture(pictures, path):
    headers = {'authority': 'downloads.fanbox.cc',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'Cache-Control': 'max-age=0',
                'Cookie': r'p_ab_id=4; p_ab_id_2=5; p_ab_d_id=1222526294; _gcl_au=1.1.541270579.1701743261; privacy_policy_agreement=6; FANBOXSESSID=81697504_VK2nc6eCbAH6uwAz1WuOyyJ3Hlr28BNe; privacy_policy_notification=0; _gid=GA1.2.1743881840.1704190047; _ga=GA1.1.2111706231.1701743261; _ga_D9TLP3EFER=GS1.1.1704333525.24.1.1704337527.40.0.0',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': "Windows",
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'}
    for k, v in pictures.items():
        r = requests.get(v, headers=headers)
        print(f'正在保存到{path / k}---')
        with open(path / k, 'wb') as file:
            file.write(r.content)


def make_path(path):
    if path.exists():
        path.rmdir()    # 如果文件夹已存在，就删除文件夹
    path.mkdir()        # 创建文件夹
    return path


def update(creator):
    root = Path(creator)
    with open(root / 'latest_post.txt', 'r') as latest:
        last_id = latest.read()
    dat0 = download(last_id)
    # print(dat0)
    picture, next_id = analysis(dat0)

    # 如果没有下一篇文章的ID，就结束
    if next_id == 0:
        print(f'{last_id}是最新')
        pass
    # 如果有下一篇文章id，就更新最后的这篇，进入循环
    else:
        # 更新last_id
        pat = root / last_id / f'{last_id}.json'
        if not pat.exists():                                                 # 如果不存在，创建该文件
            Path.mkdir(root / last_id)
            Path.touch(pat)

        with open(pat, 'w', encoding='utf-8') as upd:
            json.dump(dat0, upd, indent=4, ensure_ascii=False)

        # 遍历循环，下载下一篇post
        while next_id != 0:
            this_id = next_id
            print(f'正在下载{this_id}')
            dat1 = download(this_id)
            pictures, next_id = analysis(dat1)

            path = make_path(root / this_id)

            with open(path / f'{this_id}.json', 'w', encoding='utf-8') as new:
                json.dump(dat1, new, indent=4, ensure_ascii=False)
            if len(pictures) != 0:
                download_picture(pictures, path)

            with open(root / 'latest_post.txt', 'w') as latest:
                latest.write(this_id)


def record(creator):
    f = open(Path(creator) / 'directory.txt', 'w', encoding='utf-8')
    for root, dirs, files in os.walk(creator):
        if 'pictures' not in root:
            for file in files:
                if not file.endswith('.txt') and not file.endswith('.json'):
                    path = os.path.join(root, file)
                    # print(path)
                    f.write(path + '\n')
    f.close()


def move(creator):
    with open(Path(creator) / 'directory.txt', 'r', encoding='utf-8') as f:
        r = [i.strip('\n') for i in f.readlines()]
    directory = Path(creator) / 'pictures'
    if not directory.exists():
        Path.mkdir(directory)
    for file in tqdm(r):
        shutil.copy(file, directory)


if __name__ == '__main__':
    cookie = ''
    creator = 'mm'
    init(creator)
    update(creator)
    record(creator)
    # move(cr)
