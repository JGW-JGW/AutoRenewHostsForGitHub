# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time    : 2022-03-27 10:29
# Author  : Seto.Kaiba
import time
from pprint import pprint
from typing import List, Dict
import random as rd
import math
import datetime as dt
import re
from abc import ABCMeta, abstractmethod
import requests
import os
import shutil
import re

"""
特别鸣谢 521xueweihan 的 GitHub520

其中提供了服务器地址可以获取最新的 hosts 列表

自动更新hosts，以更快地加载GitHub
"""

# hosts 绝对路径
hosts_absname = 'C://Windows//System32//drivers//etc//hosts'
hosts_dirname = os.path.dirname(hosts_absname)
hosts_basename = os.path.basename(hosts_absname)

# 备份原始文件
shutil.copy(hosts_absname, '{}.bak.{}'.format(
    hosts_absname,
    dt.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
))

# 轮询备份文件，如果备份文件总大小超出 size_max，则删除旧的备份文件，直到备份文件总大小严格小于 size_low
size_max = 10485760  # 单位：字节，10 MB
size_low = 5242880  # 单位：字节，5 MB
total_bak_size = 0
hosts_bak_list = []
for filename in os.listdir(hosts_dirname):
    if re.compile(hosts_basename + '\.bak\.[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}').match(filename):
        tmp = os.path.join(hosts_dirname, filename)
        total_bak_size += os.path.getsize(tmp)
        hosts_bak_list.append(tmp)

if total_bak_size > size_max:
    hosts_bak_list.sort()
    for item in hosts_bak_list:
        total_bak_size -= os.path.getsize(item)
        os.remove(item)
        if total_bak_size < size_low:
            break

# 获取最新hosts文本内容
response = requests.get('https://raw.hellogithub.com/hosts')
while response.status_code != 200:
    time.sleep(rd.randint(1, 10))
    response = requests.get('https://raw.hellogithub.com/hosts')

latest_hosts = response.text

hosts_tmpname = '{}.tmp'.format(hosts_absname)
begin_keyword_count = 0
end_keyword_count = 0
with open(hosts_absname, 'r') as f_old:
    with open(hosts_tmpname, 'w+') as f_new:
        renew_flag = False  # 记录是否已经更新了最新hosts
        for line in f_old:
            if re.compile('# GitHub520 Host Start').match(line):
                begin_keyword_count += 1

            if begin_keyword_count == end_keyword_count:  # 两数相等说明要么还没遇到，要么已经成对遇到了开始和结束标记
                f_new.write(line)
                continue

            if re.compile('# GitHub520 Host End').match(line):
                end_keyword_count += 1

            if not renew_flag and begin_keyword_count > end_keyword_count:  # 说明遇到了开始标记 或 还没完全匹配上所有结束标记
                renew_flag = True
                f_new.writelines(latest_hosts)

os.remove(hosts_absname)
os.rename(hosts_tmpname, hosts_absname)

# pyinstaller --clean --noconfirm -D main.py
