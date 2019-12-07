#!/usr/bin/python3
# coding=utf-8
import requests
import logging
import xlwt
import sys

baseurl = 'https://hnu.bysjy.com.cn/module/getcareers?start_page=11&keyword=&type=inner&day=&count=9999&start=1'
logging.basicConfig(level=logging.DEBUG, format='')


# 直接获取全量数据
def get_data(url):
    json_data = requests.get(url)
    data_list = json_data.json()['data']
    return data_list


def create_sheet(work_book):
    sheet_ = work_book.add_sheet('招聘数据')
    sheet_.write(0, 0, '时间')
    sheet_.write(0, 1, '地点')
    sheet_.write(0, 2, '公司名称')
    sheet_.write(0, 3, '招聘会')
    sheet_.write(0, 4, '专业要求')
    sheet_.write(0, 5, '企业性质')
    sheet_.write(0, 6, '企业行业')
    sheet_.write(0, 7, '详细信息')
    return sheet_


def write_sheet(sheet1, data_list):
    count = 1
    for i in data_list:
        sheet1.write(count, 0, i['meet_day'] + i['meet_time'])
        sheet1.write(count, 1, i['address'])
        sheet1.write(count, 2, i['company_name'])
        sheet1.write(count, 3, i['meet_name'])
        sheet1.write(count, 4, i['professionals'])
        sheet1.write(count, 5, i['company_property'])
        sheet1.write(count, 6, i['industry_category'])
        sheet1.write(count, 7, 'https://hnu.bysjy.com.cn/detail/career?id=' + i['career_talk_id'])
        count = count + 1


# 将json的数据结构类型转换成str数据类型，csv格式
def json_to_value_list(json_data):
    values = json_data.values()
    return list_to_csvstr(values)


# 拼接json的value s值列表，转换成str数据类型
def list_to_csvstr(values):
    str_list = list(values)
    str_ = str(str_list)[1:-1]
    str_ = str_.replace('\'', '')
    return str_+'\n'


def create_csv(path='湖南大学招聘信息.csv'):
    data_list = get_data(baseurl)
    columns_list = list(data_list[0].keys())
    columns = list_to_csvstr(columns_list)
    fin = open(path, 'w', encoding='utf-8')
    fin.writelines(columns)
    fin.close()
    for data in data_list:
        with open(path, 'a', encoding='utf-8') as fin_2:
            fin_2.writelines(json_to_value_list(data))


def create_excel(path='湖南大学招聘信息.xls'):
    work_book = xlwt.Workbook()
    sheet_1 = create_sheet(work_book)
    write_sheet(sheet_1, get_data(baseurl))
    work_book.save(path)


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
