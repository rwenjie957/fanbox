import json
from pathlib import Path


#   如果文件夹不存在，创建文件夹，否则返回文件路径
def make_path(path):
    _path = Path(path)
    if not _path.is_dir():
        Path.mkdir(_path)
    return _path


def analysis(post):
    _prev, _next = '', ''
    if isinstance(post['body']['prevPost'], dict):
        _prev = post['body']['prevPost']['id']
    if isinstance(post['body']['nextPost'], dict):
        _next = post['body']['nextPost']['id']

    files = {}
    if body := post['body']['body']:
        if image_map := body.get('imageMap', None):
            for v in image_map.values():
                name = '.'.join((v['id'], v['extension']))
                files[name] = v['originalUrl']
        if image_map := body.get('images', None):
            for v in image_map:
                name = '.'.join((v['id'], v['extension']))
                files[name] = v['originalUrl']
        if file_map := body.get('fileMap', None):
            for v in file_map.values():
                name = '.'.join((v['id'], v['extension']))
                files[name] = v['url']
    else:
        print('文章可能未解锁或者不可访问')
    return _prev, _next, files                 # images:{filename:url}


if __name__ == '__main__':
    with open('config.json', 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    cookies = cfg['cookies']