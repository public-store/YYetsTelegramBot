# -*- coding: utf-8 -*-
import requests
import config
import random
import json


def show_resource(name):
    """
    搜索资源用的
    :param name:
    :return:
    """
    url = "http://pc.zmzapi.com/index.php"

    params = {
        "g": "api/pv3",
        "m": "index",
        "accesskey": "519f9cab85c8059d17544947k361a827",
        "a": "search",
        "k": "{}".format(name)
    }
    headers = {
        'User-Agent': '{}'.format(random.choice(config.UserAgent))
    }

    response = requests.request("GET", url, params=params, headers=headers)
    config.logger1.info("search_resource 查询内容:{}，返回结果:{}".format(name, response.text))
    text = json.loads(response.text)
    # 处理返回数据
    if len(text['data']) == 0:
        config.logger1.warning("search_resource 查询内容:{}，返回结果空，查询无结果")
        return None
    else:
        data = []
        for item in text['data']:
            poster_url = item.get('poster')
            id = item.get('id')
            cnname = item.get('cnname')
            channel_cn = item.get('channel_cn')
            data.append([id, poster_url, cnname, channel_cn])
        return data


def search_resource(video_id):
    url = "http://pc.zmzapi.com/index.php"

    params = {
        "g": "api/pv3",
        "m": "index",
        "client": "5",
        "accesskey": "519f9cab85c8059d17544947k361a827",
        "a": "search",
        "id": "{}".format(video_id)
    }
    headers = {
        'User-Agent': '{}'.format(random.choice(config.UserAgent))
    }

    response = requests.request("GET", url, params=params, headers=headers)
    config.logger1.info("get_video_links 查询资源ID:{}，返回结果:{}".format(name, response.text))
    text = json.loads(response.text)
    # 处理返回数据
    if len(text['status']) != 0:
        config.logger1.warning("get_video_links 查询ID:{}，无下载资源提供")
        return None
    else:
        data = []
        for item in text['data'].get('list'):
            episodes = item['episodes']

        return data


def download_poster(name):
    """
    下载视频海报
    :param name:
    :return:
    """
    data = show_resource(name)
    if data is not None:
        img_data = []
        for i in data:
            poster_url = i[1]
            cnname = i[2]
            channel_cn = i[3]
            headers = {
                'User-Agent': '{}'.format(random.choice(config.UserAgent))
            }
            response = requests.request("GET", poster_url, headers=headers, verify=False)
            if response.status_code == 200:
                img_data.append([channel_cn, cnname, response.content])
                config.logger1.info("download_poster channel_cn:{},cnname:{} 提交下载任务正常".format(channel_cn, cnname))
            else:
                config.logger1.warning("download_poster 提交下载任务异常，返回结果:{}".format(response.text))
        return img_data
    else:
        config.logger1.warning("download_poster 搜索资源无结果")
        return None


if __name__ == '__main__':
    name = "硅谷"
    download_poster(name)