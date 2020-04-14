import requests
from bs4 import BeautifulSoup
import os
import time
import json

all_url = 'http://www.mzitu.com'

#http请求头
header = {
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    'Referer': 'http://www.mzitu.com'
               }
#更新referer字段
def update_header(referer):
    header['Referer'] = '{}'.format(referer)

#保存地址
path = 'I:\\mzitu\\'

#记录文件
data = 'I:\\mzitu\\.data'
 
# 获取代理IP
def proxies_get():
    for i in range(0,50):
        html = requests.get("http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=e3929724e95a4eeabf3db27a122aae87&orderno=YZ20204141284KibJG8&returnType=2&count=1")
        result = json.loads(html.text)
        ip = result.get('RESULT')[0].get('ip')+':'+result.get('RESULT')[0].get('port')
        proxies = {
            'http': 'http://' + ip,
            'https': 'https://' + ip,
        }
        try:
            response = requests.get('http://httpbin.org/get', proxies=proxies)
            return proxies
        except requests.exceptions.ConnectionError as e:
            print('Errorip'+str(i), e.args)

#读取保存记录
def get_log(file):
    page = 1
    line = 0
    try:
        with open(file, 'r') as f:
            f_data = f.readline()
            page, line = [int(i) for i in f_data.split('|')]
    except Exception as e:
        print(e)
        print('读取记录失败，从初始开始')
    return page, line


#保存记录
def put_log(file, page, line):
    try:
        with open(file, "w") as f:
            f.write('{}|{}'.format(page, line))
    except Exception as e:
        print('保存记录失败：[{}]'.format(e))


#找寻最大页数
def find_max_page(proxies_one):
    start_html = requests.get(all_url, headers=header,proxies = proxies_one)
    soup = BeautifulSoup(start_html.text, "html.parser")
    page = soup.find_all('a', class_='page-numbers')
    max_page = page[-2].text
    max_page = int(max_page)
    return max_page

if __name__ == "__main__":
    same_url = 'http://www.mzitu.com/page/'
    proxies_one = proxies_get()
    max_page = find_max_page(proxies_one)
    page, line = get_log(data)
    print('从{}页，{}行开始缓存'.format(page, line))

    for n in range(page, int(max_page)+1):
        ul = same_url+str(n)
        start_html = requests.get(ul, headers=header,proxies = proxies_one)
        soup = BeautifulSoup(start_html.text, "html.parser")
        all_a = soup.find('div', class_='postlist').find_all('a', target='_blank')
        for lines in range(line, len(all_a)):
            a = all_a[lines]
            title = a.get_text() #提取文本
            if(title != ''):
                print("准备扒取："+title)

                #win不能创建带？的目录
                if(os.path.exists(path+title.strip().replace('?',''))):
                    print('目录已存在')
                    flag = 1
                else:
                    os.makedirs(path+title.strip().replace('?',''))
                    flag = 0
                os.chdir(path + title.strip().replace('?', ''))
                href = a['href']
                html = requests.get(href, headers=header,proxies = proxies_one)
                mess = BeautifulSoup(html.text, "html.parser")
                # 最大也在class='pagenavi'div中的第6个span
                pic_max = mess.find("div", class_='pagenavi').find_all('span')
                pic_max = pic_max[6].text #最大页数
                if(flag == 1 and len(os.listdir(path+title.strip().replace('?',''))) >= int(pic_max)):
                    print('已经保存完毕，跳过')
                    continue
                num=1
                while (num <=int(pic_max)):
                    num=num+1
                    while True:
                        pic = href+'/'+str(num)

                        try:
                            html = requests.get(pic, headers=header,proxies = proxies_one)
                        except requests.exceptions.ConnectionError as e:
                            num=num-1
                            print(str(e))
                            proxies_one = proxies_get()
                            continue
                        mess = BeautifulSoup(html.text, "html.parser")
                        pic_url = mess.find('img', alt=title)
                        if(pic_url):
                            break
                    print(pic_url['src'])
                    update_header(pic_url['src'])                   
                    try:
                        html = requests.get(pic_url['src'], headers=header,proxies = proxies_one,timeout=3)
                    except requests.exceptions.ConnectionError as e:
                        num=num-1
                        print(str(e))
                        proxies_one = proxies_get()
                        continue
                    file_name = pic_url['src'].split(r'/')[-1]
                    f = open(file_name, 'wb')
                    f.write(html.content)
                    f.close()
                put_log(data, n, lines)
                time.sleep(0.1)
        print('第',n,'页完成')
        line = 0
        time.sleep(5)
