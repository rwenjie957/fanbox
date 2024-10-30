from idlelib.iomenu import encoding

from utils import *
from pathlib import Path
import json


config_file = Path('config.json')
with open(config_file, 'r', encoding='utf-8') as configfile:
    config = json.load(configfile)
cookies = config['cookies']
creator = config['creator']


log_file = Path('log.json')
if not log_file.exists():
    Path.touch(log_file)
    log = {}
else:
    with open(log_file, 'r', encoding='utf-8') as logfile:
        log = json.load(logfile)

# 如果config中没有creator信息，则初始化creator为空字典
if not log.get(creator, None):
    log[creator] = {}

save_path = Path(creator)
if not save_path.is_dir():
    Path.mkdir(save_path)


# 搜索之前的文章
def prev_search(post_id):
    post_data = download(cookies, post_id)
    _prev, _next, images = analysis(post_data)          # 获取当前文章的所有图片链接和前后文章id
    try:
        while post_id:
            temp_log = log[creator].get(post_id, {})    # temp_log  {'status':'locked','pictures':{}}
            if images:
                temp_log['status'] = 'unlocked'
                d1 = DownloadPicture(save_path, post_id, cookies, images, temp_log)
                log[creator].update({post_id:d1.log})
                print(f"{post_id}已下载完毕")
            else:
                temp_log['status'] = 'locked'
                log[creator].update({post_id:temp_log})

            post_id = _prev
            post_data = download(cookies, post_id)
            _prev, _next, images = analysis(post_data)
    except Exception as e:
        print(e)
    finally:
        with open('log.json', 'w', encoding='utf-8') as _log:
            json.dump(log, _log, ensure_ascii=False, indent=4)


def next_search(post_id):
    post_data = download(cookies, post_id)
    with open(Path(creator) / post_id / f'{post_id}.json', 'w', encoding='utf-8') as done:
        json.dump(post_data, done, indent=4, ensure_ascii=False)
    _prev, _next, images = analysis(post_data)          # 获取当前文章的所有图片链接和前后文章id
    if not _next:                       # 如果没有新增文章
        print('没有新增动态')
    else:
        try:
            while post_id:
                temp_log = log[creator].get(post_id, {})    # temp_log  {'status':'locked','pictures':{}}
                if images:
                    temp_log['status'] = 'unlocked'
                    d1 = DownloadPicture(save_path, post_id, cookies, images, temp_log)
                    d1.multi_download()
                    log[creator].update({post_id:d1.log})

                else:
                    temp_log['status'] = 'locked'
                    log[creator].update({post_id:temp_log})

                config['latest_post'] = post_id                # 更新最新的文章id
                post_id = _next
                post_data = download(cookies, post_id)
                _prev, _next, images = analysis(post_data)
        except Exception as e:
            print(e)
        finally:
            with open('log.json', 'w', encoding='utf-8') as _log:
                json.dump(log, _log, ensure_ascii=False, indent=4)
            with open('config.json', 'w', encoding='utf-8') as config_:
                json.dump(config, config_, ensure_ascii=False, indent=4)


next_search(config['latest_post'])