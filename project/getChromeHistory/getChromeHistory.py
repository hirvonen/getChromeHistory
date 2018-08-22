#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 统计Chrome访问历史记录
# Ver 1.0
import re
import chardet
import urllib
from lxml import etree
import zlib
import ssl
# from urllib.request import urlopen

import os
import sqlite3
import operator
from collections import OrderedDict
import matplotlib.pyplot as plt


def get_title_xpath(Html):
    '''
    用xpath抽取网页Title
    '''
    Html_encoding = chardet.detect(Html)['encoding']
    page = etree.HTML(Html, parser=etree.HTMLParser(encoding=Html_encoding))
    title = page.xpath('/html/head/title/text()')
    try:
        title = title[0].strip()
    except Exception as reason:
        print('get_title_xpath exception reason: %s' % reason)
    return title


def parse(url):
    try:
        parsed_url_components = url.split('//')
        sublevel_split = parsed_url_components[1].split('/', 1)
        sublevel_split[0] = parsed_url_components[0] + '//' + sublevel_split[0]
        # sublevel_split[0] = 'http://' + sublevel_split[0]
        domain = sublevel_split[0]
        return domain
    except IndexError:
        print('parse URL format error!')


def analyze(results):
    prompt = input("[.] Type <c> to print or <p> to plot\n[>] ")
    if prompt == "c":
        with open('./history.txt', 'w') as f:
            for site, count in sites_count_sorted.items():
                # 抽取并写入网页title
                title = "Unknown"
                try:
                    ssl._create_default_https_context = ssl._create_unverified_context
                    # 解决403 Forbidden的问题，添加UserAgent
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
                        }
                    req = urllib.request.Request(url=site, headers=headers)
                    html = urllib.request.urlopen(req).read()
                except Exception as error:
                    print("urlopen error: %s with error %s" % (site, error))
                    f.write(site+'\t'+str(title)+'\t'+str(count)+'\n')
                    continue
                try:
                    title = get_title_xpath(html)
                except Exception as error:
                    print("fetch title error '%s' with error %s" %
                          (site, error))
                    f.write(site+'\t'+str(title)+'\t'+str(count)+'\n')
                    continue
                try:
                    f.write(str(site)+'\t'+str(title)+'\t'+str(count)+'\n')
                except Exception as error:
                    print("write error %s with error %s" % (site, error))
                    continue
            f.close()
    elif prompt == "p":
        key = []
        value = []
        for k, v in results.items():
            key.append(k)
            value.append(v)
        n = 25
        X = range(n)
        Y = value[:n]
        plt.bar(X, Y, align='edge')
        plt.xticks(rotation=45)
        plt.xticks(X, key[:n])
        for x, y in zip(X, Y):
            plt.text(x+0.4, y+0.05, y, ha='center', va='bottom')
        plt.show()
    else:
        print("[.] Uh?")
        quit()


if __name__ == '__main__':
    # path to user's history database (Chrome)
    # data_path=r'C:\Users\zhanglei\AppData\Local\Google\Chrome\User Data\Default'
    data_path = r'F:\python\Default'
    files = os.listdir(data_path)

    history_db = os.path.join(data_path, 'history')

    # querying the db
    c = sqlite3.connect(history_db)
    cursor = c.cursor()
    select_statement = "SELECT urls.url, urls.visit_count FROM urls, visits WHERE urls.id = visits.url;"
    cursor.execute(select_statement)

    results = cursor.fetchall()  # tuple

    sites_count = {}

    for url, count in results:
        url = parse(url)
        if url in sites_count:
            sites_count[url] += 1
        else:
            sites_count[url] = 1

    sites_count_sorted = OrderedDict(
        sorted(sites_count.items(), key=operator.itemgetter(1), reverse=True))

    analyze(sites_count_sorted)
