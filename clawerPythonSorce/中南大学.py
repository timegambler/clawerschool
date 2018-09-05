#!/usr/bin/python3
#coding=utf-8
import requests
import xlwt
import json
import logging
import bs4
from bs4 import BeautifulSoup
#初始化日志保存路劲，及格式
logging.basicConfig(filename='log.txt',level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('requests').setLevel(logging.WARNING)#禁用requests的日志

#初始化表格
workbook = xlwt.Workbook()
sheet1 = workbook.add_sheet('list')
sheet1.write(0,0,'时间')
sheet1.write(0,1,'地点')
sheet1.write(0,2,'公司名称')
sheet1.write(0,3,'职位名称')
sheet1.write(0,4,'教育水平')
sheet1.write(0,5,'专业要求')
sheet1.write(0,6,'空缺数量')
sheet1.write(0,7,'详细信息')

#初始化地址
json_all_url = 'http://jobsky.csu.edu.cn/Home/SearchDateAllMonth'
dt1={'Date':'2018-09-04'}
post_data = requests.post(json_all_url,data=dt1)
json_data = post_data.json()
logging.debug(type(json_data))
'''with open('json.txt','w') as fileTxt:
    for i in json_data:
        fileTxt.write(str(i)+'\n')    
'''
basic_html_url = 'http://jobsky.csu.edu.cn/Home/ArticleDetails/'

counter_all = 1
for data in json_data:
    company_Id=data['NewsID']
    #logging.debug('the commpanyID is:'+company_Id)
    html_url=basic_html_url+company_Id
#html_url=basic_html_url+'13713'#static url,please delete and repaire after you have used it
    
    html_txt = requests.get(html_url)
#  logging.debug('the web site using code is:'+str(html_txt.status_code))
    bs = BeautifulSoup(html_txt.text,'lxml')
    
    #get the commpanyName
    
    list_soup_CN = bs.find('h1',attrs={'class':'text-center title'})
    try:    
        advertise_company_name=list_soup_CN.getText()
        sheet1.write(counter_all,2,advertise_company_name)
    except:
        logging.debug("the url"+html_url+'has some problem')
    #get the time and place
    try:
        list_soup_TP = bs.find('div',attrs={'id':'placeAndTime'})
        advertise_time=list_soup_TP.find('p',attrs={'class':'text-center time'}).getText()
        advertise_place=list_soup_TP.find('p',attrs={'class':'text-center place'}).getText()
        sheet1.write(counter_all,0,advertise_time)
        sheet1.write(counter_all,1,advertise_place)
    except:
        logging.debug("the url"+html_url+'has some problem')
    
    try:     
        list_soup_demand = bs.find('table',attrs={'class':'table table-bordered'})
        list_td = list_soup_demand.find_all('td')
        counter_even = 0#use to counter ,so that we can find the number of td,and get we need data
        #we can get the useful data by looking the source
        for td in list_td:
            if counter_even==1 :
                sheet1.write(counter_all,3,td.getText())
            if counter_even==3 :
                sheet1.write(counter_all,4,td.getText())
            if counter_even==5 :
                sheet1.write(counter_all,5,td.getText())
            if counter_even==7 :
                sheet1.write(counter_all,6,td.getText())
            counter_even =counter_even+1
        sheet1.write(counter_all,7,html_url)
        counter_all+=1
    except:
        logging.debug("the url"+html_url+'has some problem')
    #保存文件
    workbook.save('中南大学招聘信息.xlsx')