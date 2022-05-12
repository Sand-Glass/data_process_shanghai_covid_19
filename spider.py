import calendar
from urllib.parse import urlencode
import requests
from pyquery import PyQuery as pq
import time
import os
import csv
import json

base_url = 'https://m.weibo.cn/api/container/getIndex?'

headers = {
    'Host': 'm.weibo.cn',
    'Referer': 'https://m.weibo.cn/u/2830678474',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}


class SaveCSV(object):

    def save(self, keyword_list, path, item):
        """
        保存csv方法
        :param keyword_list: 保存文件的字段或者说是表头
        :param path: 保存文件路径和名字
        :param item: 要保存的字典对象
        :return:
        """
        try:
            # 第一次打开文件时，第一行写入表头
            if not os.path.exists(path):
                with open(path, "w", newline='', encoding='utf_8_sig') as csvfile:  # newline='' 去除空白行
                    writer = csv.DictWriter(csvfile, fieldnames=keyword_list)  # 写字典的方法
                    writer.writeheader()  # 写表头的方法

            # 接下来追加写入内容
            with open(path, "a", newline='', encoding='utf_8_sig') as csvfile:  # newline='' 一定要写，否则写入数据有空白行
                writer = csv.DictWriter(csvfile, fieldnames=keyword_list)
                writer.writerow(item)  # 按行写入数据
                print("^_^ write success")

        except Exception as e:
            print("write error==>", e)
            # 记录错误数据
            with open("error.txt", "w") as f:
                f.write(json.dumps(item) + ",\n")
            pass


def get_page(page, title):  # 得到页面的请求，params是我们要根据网页填的，就是下图中的Query String里的参数
    params = {
        'containerid': '100103type=1&q=' + title,
        'page': page,  # page是就是当前处于第几页，是我们要实现翻页必须修改的内容。
        'type': 'all',
        'queryVal': title,
        'featurecode': '20000320',
        'luicode': '10000011',
        'lfid': '106003type=1',
        'title': title
    }
    url = base_url + urlencode(params)
    print(url)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(page)
            return response.json()
    except requests.ConnectionError as e:
        print('Error', e.args)


def convert_date(date_str):
    date_list = date_str.split()
    month = list(calendar.month_abbr).index(date_list[1])
    date_cur = date_list[5] + '-' + str(month) + '-' + date_list[2]
    return date_cur


# 解析接口返回的json字符串
def parse_page(json, label):
    res = []
    if json:
        items_1 = json.get('data')['cards']
        items = json.get('data').get('cards')
        for i in items:
            if i == None:
                continue
            i_key = i.keys()
            item = i.get('card_group')[0].get('mblog')
            # item = i.get('mblog')

            if item == None:
                continue
            weibo = {}
            weibo['id'] = item.get('id')
            date = item.get('created_at')
            weibo['date'] = convert_date(date)
            weibo['label'] = label
            weibo['text'] = pq(item.get('text')).text().replace(" ", "").replace("\n", "")
            res.append(weibo)
    return res


if __name__ == '__main__':
    title = '上海疫情'
    # title = input("请输入搜索关键词：")
    path = "data/article.csv"
    item_list = ['id', 'date', 'text', 'label']
    s = SaveCSV()
    for page in range(1, 600):  # 循环页面
        try:
            time.sleep(1)  # 设置睡眠时间，防止被封号
            json = get_page(page, title)
            results = parse_page(json, title)
            if requests == None:
                continue
            for result in results:
                if result == None:
                    continue
                print('result')
                print(result)
                s.save(item_list, path, result)
        except TypeError:
            print("完成")
            continue
