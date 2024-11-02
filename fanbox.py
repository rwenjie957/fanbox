from utils import *
from pathlib import Path
import json


class Fanbox:
    def __init__(self, config, log, save_path_root='.'):
        self.config = config
        self.cookies = config['cookies']
        self.post_id = config['latest_post']
        self.creator = config['creator']
        self.log = log
        self.save_path = make_path(Path(save_path_root) / config['creator'])

        # 如果config中没有creator信息，则初始化creator为空字典
        if not self.log.get(self.creator):
            self.log[self.creator] = {}

# 搜索之前的文章
    def prev_search(self, mode = 'multiple'):
        post_id = self.post_id                              # 给局部变量赋值类变量的post_id,由于向前搜索，不影响类中原本post_id
        post_data = download(self.cookies, post_id)
        _prev, _next, images = analysis(post_data)          # 获取当前文章的所有图片链接和前后文章id
        try:
            while post_id:
                post_id_directory = make_path(self.save_path / post_id)
                with open(post_id_directory / f'{post_id}.json', 'w', encoding='utf-8') as done:
                    json.dump(post_data, done, indent=4, ensure_ascii=False)

                temp_log = self.log[self.creator].get(post_id, {})    # temp_log  {'status':'locked','pictures':{}}
                if images:
                    temp_log['status'] = 'unlocked'
                    d1 = DownloadPicture(self.save_path, post_id, self.cookies, images, temp_log)
                    if mode == 'multiple':
                        d1.multi_download()
                    else:
                        d1.single_download()
                    self.log[self.creator].update({post_id:d1.log})
                    print(f"{post_id}已下载完毕")
                else:
                    temp_log['status'] = 'locked'
                    self.log[self.creator].update({post_id:temp_log})

                post_id = _prev
                post_data = download(self.cookies, post_id)
                _prev, _next, images = analysis(post_data)

        except Exception as e:
            print(e)

        finally:
            with open('log.json', 'w', encoding='utf-8') as _log:
                json.dump(self.log, _log, ensure_ascii=False, indent=4)


    def next_search(self, mode = 'multiple'):
        post_data = download(self.cookies, self.post_id)
        _prev, _next, images = analysis(post_data)          # 获取当前文章的所有图片链接和前后文章id
        if not _next:                       # 如果没有新增文章
            print('没有新增动态')
        else:
            try:
                while self.post_id:
                    post_id_directory = make_path(self.save_path / self.post_id)
                    # 当有post_id时，下载文章信息
                    with open(post_id_directory / f'{self.post_id}.json', 'w', encoding='utf-8') as done:
                        json.dump(post_data, done, indent=4, ensure_ascii=False)

                    temp_log = self.log[self.creator].get(self.post_id, {})    # temp_log  {'status':'locked','pictures':{}}
                    if images:
                        temp_log['status'] = 'unlocked'
                        d1 = DownloadPicture(self.save_path, self.post_id, self.cookies, images, temp_log)
                        if mode == 'multiple':
                            d1.multi_download()
                        else:
                            d1.single_download()
                        self.log[self.creator].update({self.post_id:d1.log})

                    else:
                        temp_log['status'] = 'locked'
                        self.log[self.creator].update({self.post_id:temp_log})

                    self.config['latest_post'] = self.post_id                # 更新最新的文章id
                    self.post_id = _next
                    post_data = download(self.cookies, self.post_id)
                    _prev, _next, images = analysis(post_data)
            except Exception as e:
                print(e)
            finally:
                with open('log.json', 'w', encoding='utf-8') as _log:
                    json.dump(self.log, _log, ensure_ascii=False, indent=4)
                with open('config.json', 'w', encoding='utf-8') as config_:
                    json.dump(self.config, config_, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    config_file = Path('config.json')
    with open(config_file, 'r', encoding='utf-8') as configfile:
        config = json.load(configfile)

    log_file = Path('log.json')
    if not log_file.exists():
        Path.touch(log_file)
        log = {}
    else:
        with open(log_file, 'r', encoding='utf-8') as logfile:
            log = json.load(logfile)

    f = Fanbox(config, log)
    f.next_search()