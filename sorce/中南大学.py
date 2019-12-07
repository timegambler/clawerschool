#!/usr/bin/python3
# coding=utf-8
import sys
import traceback
import xlwt
import requests
import logging
import json
import datetime
from dateutil.relativedelta import relativedelta
from lxml import etree
import urllib3

# 初始化日志保存路劲，及格式
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.getLogger('requests').setLevel(logging.WARNING)  # 禁用requests的日志

# 初始化爬取网页链接地址
base_url = 'http://career.csu.edu.cn/default/date'

# domain,招聘网站域名
b_url = 'http://career.csu.edu.cn'

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


# 用于获取招聘所有网址链接的信息
def get_post_data(url):
    json_text = read_json(setting_path)
    month_list = get_month(json_text['began_date'], json_text['end_date'])
    post_data_list = []
    for mon in month_list:
        dt1 = {'year': str(mon.year), 'month': str(mon.month)}
        post_data = requests.post(url, data=dt1)
        # print(post_data.text)
        json_data = post_data.json()
        post_data_list.append(json_data)
        # print(json_data)
    return post_data_list


# 用于处理爬取的信息， 参数url为招聘网站前缀，post_data_list为爬取的总信息，返回拼接招聘网站链接
def get_url_data_list(basicurl, post_data_list):
    url_list = []
    # print(len(data_list))
    for data_ in post_data_list:
        keys_list = data_.keys()
        for key in keys_list:
            if data_[key]:
                try:
                    selector = etree.HTML(data_[key])
                    item = selector.xpath('//a[@target="_blank"]/@href')
                    for url in item:
                        if 'teachin' in url:
                            url_list.append(basicurl + url)
                except Exception as err:
                    print(err)
        # print(url_list)
    return url_list


# 爬取招聘网站相关具体信息
def get_career_data(url):
    http = urllib3.PoolManager()
    res = http.request('get', url)
    html = res.data.decode('utf-8')
    return html


# 获取网页内容并解析需要的数据，返回字典
def get_data(basicurl):
    data_list = []
    post_data_list = get_post_data(base_url)
    url_list = get_url_data_list(basicurl, post_data_list)
    for url in url_list:
        data_line = {}
        html = get_career_data(url)
        selector = etree.HTML(html)
        # 公司名称
        title = selector.xpath('//*[@id="mn"]/div[1]/h1/text()')
        # 单位性质
        enterprice_propertice = selector.xpath('//*[@id="mn"]/ul[1]/li[1]/span/text()')
        # 企业行业
        enterprice_industry = selector.xpath('//*[@id="mn"]/ul[1]/li[2]/span/text()')
        # 单位规模
        enterprice_size = selector.xpath('//*[@id="mn"]/ul[1]/li[3]/span/text()')
        # 宣讲时间
        preach_time = selector.xpath('//*[@id="mn"]/ul[2]/li[1]/span/text()')
        # 宣讲地点
        meet_place = selector.xpath('//*[@id="mn"]/ul[2]/li[4]/span/text()')
        data_line = {'title': title, 'enterprice_propertice': enterprice_propertice,
                     'enterprice_industry': enterprice_industry,
                     'enterprice_size': enterprice_size, 'preach_time': preach_time, 'meet_place': meet_place,
                     'url': url}
        data_list.append(data_line)
    # 职位名称	需求人数	需求专业	薪资	学历
    # information_list = selector.xpath('//*[@id="vTab1"]/table/tbody/tr[1]/td')
    # print(title, enterprice_propertice, enterprice_industry, enterprice_size, preach_time)
    return data_list


# 创建工作表
def create_sheet(work_book):
    sheet = work_book.add_sheet('list')
    sheet.write(0, 0, '时间')
    sheet.write(0, 1, '地点')
    sheet.write(0, 2, '公司名称')
    sheet.write(0, 3, '企业性质')
    sheet.write(0, 4, '企业行业')
    sheet.write(0, 5, '企业规模')
    sheet.write(0, 6, '具体信息')
    return sheet


# 将数据写入到Excel中
def write_sheet(sheet, data_list):
    counter = 0
    try:
        for i in data_list:
            counter = counter + 1
            sheet.write(counter, 0, i['preach_time'])
            sheet.write(counter, 1, i['meet_place'])
            sheet.write(counter, 2, i['title'])
            sheet.write(counter, 3, i['enterprice_propertice'])
            sheet.write(counter, 4, i['enterprice_industry'])
            sheet.write(counter, 5, i['enterprice_size'])
            sheet.write(counter, 6, i['url'])
    except Exception as e:
        print(e)
        traceback.print_exc()
    return sheet


# 创建excel文件
def create_excel(path='湖南大学招聘信息.xls'):
    work_book = xlwt.Workbook()
    sheet_1 = create_sheet(work_book)
    write_sheet(sheet_1, get_data(b_url))
    work_book.save(path)


def json_to_value_list(json_data):
    values = json_data.values()
    return list_to_csvstr(values)


def list_to_csvstr(values):
    str_list = list(values)
    str_ = str(str_list)[1:-1]
    str_ = str_.replace('\'', '')
    return str_+'\n'


def create_csv(path='湖南大学招聘信息.csv'):
    data_list = get_data(b_url)
    columns_list = list(data_list[0].keys())
    columns = list_to_csvstr(columns_list)
    fin = open(path, 'w', encoding='utf-8')
    fin.writelines(columns)
    fin.close()
    for data in data_list:
        with open(path, 'a', encoding='utf-8') as fin_2:
            fin_2.writelines(json_to_value_list(data))


create_excel('中南大学招聘信息.xls')


def main():
    if len(sys.argv) < 2:
        create_csv()
    elif len(sys.argv) == 2:
        if sys.argv[1] == 1:
            create_excel()
        else:
            create_csv()
    else:
        if sys.argv[1] == 1:
            create_excel(path=sys.argv[2])
        else:
            create_csv(path=sys.argv[2])


if __name__ == '__main__':
    main()

