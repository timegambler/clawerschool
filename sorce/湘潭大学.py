#!/usr/bin/python3
# coding=utf-8
import sys
import traceback
import requests
import logging
import xlwt
import json
import queue
import datetime
from dateutil.relativedelta import relativedelta

# basic_url = 'http://jobs.xtu.edu.cn/index/getdaycareers?day='
# 设置日志等级
logging.basicConfig(level=logging.ERROR, format='')

# url前缀
basic_url = 'http://jobs.xtu.edu.cn/index/getdaycareers?day='

# 配置文件路径
setting_path = "../settings.json"


# 读取配置文件
def read_json(path):
    with open(path, 'r', encoding="utf-8-sig") as fp:
        text = fp.read()
        return json.loads(text)


# 读取起始日期和中止日期，返回需要爬取的月份列表
def get_month(begin_date, end_date):
    time_begin = datetime.datetime.strptime(begin_date, '%Y-%m-%d')
    time_end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    # print(time_begin,time_end)
    month_list = []
    while time_begin < time_end:
        month_list.append(time_begin)
        time_begin = time_begin + relativedelta(months=1)
    return month_list


# 读取起始日期和中止日期，返回需要爬取的日期列表
def get_days(begin_date, end_date):
    month_list = get_month(begin_date, end_date)
    date_list = []
    for month in month_list:
        # print(base_url+month.strftime('%Y-%m-%d'))
        month_begin_day = month
        month_day = []
        # print('begin_day:', month_begin_day)
        while month_begin_day < month + relativedelta(months=1) or month_begin_day < month_list[-1]:
            month_day.append(month_begin_day.strftime('%Y-%m-%d'))
            month_begin_day = month_begin_day + datetime.timedelta(days=1)
            # print(month_begin_day)
        date_list.append(month_day)
    return date_list


# 输入参数为基础url，开始时间，结束时间,以月为账期，返回队列列表
def get_queue(base_url, begin_date, end_date):
    list_queue = []
    date_list = get_days(begin_date, end_date)
    for month_date_list in date_list:
        link_queue = queue.Queue(maxsize=0)  # 设置队列大小无限制
        url_list = [base_url + day for day in month_date_list]
        for link in url_list:
            link_queue.put(link)
        list_queue.append(link_queue)
    return list_queue


# print(get_queue(basic_url, '2019-01-01', '2019-1-30')[0].get())
# get_queue(basic_url,'2019-01-01','2019-5-30')


# 获取链接内容，返回列表
def get_data(url):
    clawertext = requests.get(url)
    data_list = clawertext.json()['data']
    return data_list


# 以月为账期
# 参数work_book,date表示一个文件对象和日期，创建Excel文件夹，返回包含Excel文件对象,和sheet对象列表
def creat_sheet(work_book, month):
    # work_book = xlwt.Workbook()
    sheet_ = work_book.add_sheet(month)
    sheet_.write(0, 0, '时间')
    sheet_.write(0, 1, '地点')
    sheet_.write(0, 2, '公司名称')
    sheet_.write(0, 3, '专业要求')
    sheet_.write(0, 5, '详细信息')
    return sheet_


# 将数据写入到Excel中
def write_sheet(sheet, data_list, row):
    counter = row
    try:
        for i in data_list:
            counter = counter + 1
            sheet.write(counter, 0, i['meet_day'])
            sheet.write(counter, 1, i['address'])
            sheet.write(counter, 2, i['meet_name'])
            sheet.write(counter, 3, i['professionals'])
            sheet.write(counter, 5, 'http://jobs.xtu.edu.cn/detail/career?id=' + i['career_talk_id'])
    except Exception as e:
        print(e)
        traceback.print_exc()
    return sheet


def get_data_list(base_url):
    json_settings = read_json(setting_path)
    begin_date = json_settings['began_date']
    end_date = json_settings['end_date']
    queuelist = get_queue(base_url, begin_date, end_date)
    a_month_data = []
    try:
        for que in queuelist:
            month_data = []
            while not que.empty():
                data_list = get_data(que.get())
                # print(data_list)
                month_data.append(data_list)
        a_month_data.append(month_data)
    except Exception as e:
        print(e)
        traceback.print_exc()
    return a_month_data


def list_to_csvstr(values):
    str_list = list(values)
    str_ = str(str_list)[1:-1]
    str_ = str_.replace('\'', '')
    return str_+'\n'


def json_to_value_list(json_data):
    values = json_data.values()
    return list_to_csvstr(values)


# 创建csv文件
def create_csv(path='湘潭大学招聘信息.csv'):
    a_data = get_data_list(basic_url)
    for b_data in a_data:
        for c_data in b_data:
            if c_data:
                column = list(c_data[0].keys())
                f = open(path, 'w', encoding='utf-8')
                f.write(list_to_csvstr(column))
                f.close()
                break
    for i in range(len(a_data)):
        month_data_list = a_data[i]
        with open(path, 'a', encoding='gbk') as fin:
            for day_data_list in month_data_list:
                for data in day_data_list:
                    fin.write(json_to_value_list(data))


# over it
def creat_excel(path='湘潭大学招聘信息.xls'):
    json_settings = read_json(setting_path)
    month_list = get_month(json_settings['began_date'], json_settings['end_date'])
    work_book = xlwt.Workbook()
    sheet_list = []
    a_data = get_data_list(basic_url)
    # 创建多个工作表
    try:
        for month in month_list:
            sheet_ = creat_sheet(work_book, month.strftime('%Y%m'))
            sheet_list.append(sheet_)
    except Exception as e:
        print(e)
        traceback.print_exc()
    # 在多个工作表中写入数据
    try:
        for i in range(len(month_list)):
            data_li = a_data[i]
            row = 1
            for data in data_li:
                if data:
                    write_sheet(sheet_list[i], data, row)
                    row = row + len(data)
    except Exception as e:
        print(e)
        traceback.print_exc()
    work_book.save(path)


def main():
    if len(sys.argv) < 2:
        create_csv()
    elif len(sys.argv) == 2:
        if sys.argv[1] == 1:
            creat_excel()
        else:
            create_csv()
    else:
        if sys.argv[1] == 1:
            creat_excel(path=sys.argv[2])
        else:
            create_csv(path=sys.argv[2])


if __name__ == "__main__":
    main()
