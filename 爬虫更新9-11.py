import os.path
import random,requests
import threading
import time,datetime
import json,re

import schedule
from lxml import etree
# from moviepy.editor import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from  flask import  Flask,request
from fake_useragent import UserAgent
from flask_cors import CORS

app=Flask(__name__)
CORS(app)   #支持跨域

def vedio_time(url):
    print('判断视频时长是否大于20分钟')
    print('视频url:',url)
    options = webdriver.ChromeOptions()  # 创建一个选项 最终运行按照选项执行
    options.add_argument('--headless')  # 隐藏浏览器
    driver = webdriver.Chrome(options=options)
    # 禁用webdriver检测的脚本
    script = 'Object.defineProperty(navigator, "webdriver", {get: () => false,});'
    driver.execute_script(script)
    driver.get(url)
    time.sleep(3)
    page = driver.page_source.encode('utf-8').decode('utf-8')
    time_info = re.search(r'bpx-player-ctrl-time-duration">(.*?)<', page).group(1)
    minute = time_info.split(':')[-2]
    return [time_info,minute]

def bili_list(url,page):
    options = webdriver.ChromeOptions()  # 创建一个选项 最终运行按照选项执行
    options.add_argument('--headless')  # 隐藏浏览器
    driver = webdriver.Chrome(options=options)
    # 禁用webdriver检测的脚本
    script = 'Object.defineProperty(navigator, "webdriver", {get: () => false,});'
    driver.execute_script(script)

    # 等待10s
    driver.get(url)
    time.sleep(5)

    #判断文件夹
    file_path = f'D:\MP4\\{datetime.datetime.today().strftime("%Y-%m-%d")}'
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    # 获取【首页】视频
    ls = []
    try:
        first_url = url.split('?')[0]
    except:
        first_url = url
    print('判断地址', first_url)
    if first_url == 'https://www.bilibili.com/':
        print('首页，页面默认下拉10次')
        for s in range(1, page):
            s = 500 * s
            driver.execute_script("window.scrollTo(0, arguments[0]);", s)
            time.sleep(1)
        time.sleep(3)
        page_source = driver.page_source
        html = etree.HTML(page_source)
        x = 1
        while x <= page * 3:
            x+=1
            print(x)
            try:
                print('开始')
                cover1=driver.find_element(By.XPATH, f'/html/body/div[2]/div[2]/main/div[2]/div/div[1]/div[{x}]/div[2]/a/div/div[1]/picture/img').get_attribute('src')
                # cover1 = html.xpath(f'/html/body/div[2]/div[2]/main/div[2]/div/div[1]/div[{x}]/div[2]/a/div/div[1]/picture/img/@src')
                print(cover1)
                title1 = html.xpath(f'/html/body/div[2]/div[2]/main/div[2]/div/div[1]/div[{x}]/div[2]/div/div/h3/a/text()')
                title1 = title1[0].strip()
                vedio1 = html.xpath(f'/html/body/div[2]/div[2]/main/div[2]/div/div[1]/div[{x}]/div[2]/div/div/h3/a/@href')
                vedio1 = vedio1[0].strip()
                print('title',title1, vedio1,cover1)

                if len(title1) != 0 or len(vedio1) != 0:
                    js = {'title': title1, 'vedio': vedio1, 'cover': cover1.split('@')[0]}
                    ls.append(js)

            except:
                print('错误')
                try:
                    cover2=driver.find_element(By.XPATH, f'/html/body/div[2]/div[2]/main/div[2]/div/div[1]/div[{x}]/div/div[2]/a/div/div[1]/picture/img').get_attribute('src')
                    # cover2 = html.xpath(f'/html/body/div[2]/div[2]/main/div[2]/div/div[1]/div[{x}]/div/div[2]/a/div/div[1]/picture/img/@src')
                    print(cover2)
                    title2 = html.xpath(f'/html/body/div[2]/div[2]/main/div[2]/div/div[1]/div[{x}]/div/div[2]/div/div/h3/a/text()')
                    title2 = title2[0].strip()
                    vedio2 = html.xpath(f'/html/body/div[2]/div[2]/main/div[2]/div/div[1]/div[{x}]/div/div[2]/div/div/h3/a/@href')
                    vedio2 = vedio2[0].strip()
                    print('title2',title2, vedio2,cover2)

                    if len(title2) != 0 or len(vedio2) != 0:
                        js = {'title': title2, 'vedio': vedio2, 'cover':cover2.split('@')[0]}
                        ls.append(js)
                except:
                    print('title2 规则获取失败，跳过')
                    pass

    elif re.search(r'/BV\w{10}/',first_url.split('?')[0]):  # 判断是否为单个视频
        info=vedio_time(first_url)
        if len(info[0]) > 5 or int(info[1]) > 20:
            print(f'{info[0]}超时,不做下载')
            pass

        else:
            print(f'{info[0]}时长符合,开始下载')
            print('单个视频下载')
            os.chdir('D:\BBDown-1.6.1\BBDown-1.6.1\Binary')
            os.system(f'BBDown -tv --work-dir {file_path} {first_url}')

    # 获取【鬼畜,游戏,生活,娱乐】板块首页视频地址
    else:
        print('其他类型【鬼畜,游戏,生活,娱乐】')
        # 逐渐滚动页面到底部，每次滚动的距离为500像素
        page_height = driver.execute_script("return document.body.scrollHeight")  # 获取高度
        current_height = 0
        while current_height < page_height:
            driver.execute_script("window.scrollTo(0, arguments[0]);", current_height)
            time.sleep(1)  # 可以根据需要调整滚动速度
            current_height += 500
        # driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")   # 直接拉到浏览器底部，有可能中间缓冲不过来
        time.sleep(3)
        # 获取当前页面的源代码
        page_source = driver.page_source
        html = etree.HTML(page_source)
        html1 = etree.tostring(html, encoding='utf-8').decode('utf-8')
        with open('./bilili.html', 'w', encoding='utf-8') as f:
            f.write(html1)
        for n in [2, 4, 5, 7, 8, 10]:
            for m in range(1, 9):
                print(n, m)
                try:
                    cover=driver.find_element(By.XPATH, f'/html/body/div[2]/div/main/div/div[{n}]/div/div[2]/div[{m}]/div[2]/a/div/div[1]/picture/img').get_attribute('src')
                    cover=cover.split('@')[0]
                    print('cover',cover)
                    title = html.xpath(f'/html/body/div[2]/div/main/div/div[{n}]/div/div[2]/div[{m}]/div[2]/div/div/h3/a/text()')
                    title = title[0].strip()
                    print(title)
                    vedio = html.xpath(f'/html/body/div[2]/div/main/div/div[{n}]/div/div[2]/div[{m}]/div[2]/div/div/h3/a/@href')
                    vedio = vedio[0].strip()
                    print(vedio)
                    if len(title) != 0 or len(vedio) != 0:
                        js = {'title': title, 'vedio': 'https:'+vedio, 'cover': cover.split('@')[0]}
                        ls.append(js)

                except:
                    try:
                        cover=driver.find_element(By.XPATH,f'/html/body/div[2]/div/main/div/div[{n}]/div[2]/div[{m}]/div[2]/a/div/div[1]/picture/img').get_attribute('src')
                        print(cover)
                        title=html.xpath(f'/html/body/div[2]/div/main/div/div[{n}]/div[2]/div[{m}]/div[2]/div/div/h3/a/text()')
                        title=title[0].strip()
                        print(title)
                        vedio=html.xpath(f'/html/body/div[2]/div/main/div/div[{n}]/div[2]/div[{m}]/div[2]/div/div/h3/a/@href')
                        vedio=vedio[0].strip()
                        print(vedio)
                        if len(title) != 0 or len(vedio) != 0:
                            js = {'title': title, 'vedio': 'https:'+vedio, 'cover': cover.split('@')[0]}
                            ls.append(js)
                    except:
                        print('2规则获取失败，跳过')
                        pass

    json.loads(json.dumps(ls))
    print(ls)


    for i in ls:
        print(i)
        title=i['title']
        vedio=i['vedio']
        cover=i['cover'].split('@')[0]
        print(cover)
        try:
            info = vedio_time(vedio)
            if len(info[0]) > 5 or int(info[1]) > 20:
                print(f'{info[0]}超时,不做下载')
            else:
                print(f'{info[0]}时长符合,开始下载')
                if os.path.exists(f'{file_path}\\coverimg\\{title}.jpg'):
                    print('封面已存在')
                    pass
                else:
                    print('开始下载封面')
                    with open(f'{file_path}\\coverimg\\{title}.jpg', 'wb') as f:
                        f.write(requests.get(cover).content)

                if os.path.exists(f'{file_path}\\{title}.mp4'):
                    print('文件已存在')
                    pass
                else:
                    print('开始下载')
                    os.chdir('D:\BBDown-1.6.1\BBDown-1.6.1\Binary')
                    os.system(f'BBDown -tv --work-dir {file_path} {vedio}')
        except:
            print('下载失败')
            pass
    return ls

#获取单个板块
@app.route('/one_bili',methods=['GET','POST'])
def one_url():
    print('开始获取')
    url = request.args.get('url', 'https://www.bilibili.com/?spm_id_from=333.1073.0.0')
    page = int(request.args.get('page', 10))
    bili_list(url,page)
    return '下载完成'

#获取B站全板块
@app.route('/all_bili',methods=['GET','POST'])
def all():
    ls=['https://www.bilibili.com/?spm_id_from=333.1073.0.0','https://www.bilibili.com/v/game/?spm_id_from=333.1073.0.0','https://www.bilibili.com/v/douga/?spm_id_from=333.1007.0.0',
        'https://www.bilibili.com/v/kichiku/?spm_id_from=333.1007.0.0','https://www.bilibili.com/v/life/?spm_id_from=333.1073.0.0','https://www.bilibili.com/v/ent/?spm_id_from=333.1073.0.0']
    for url in ls:
        try:
            bili_list(url,page=10)
            print(f'下载完成：{url}')

        except:
            print(f"{url}下载失败！")
            pass

    return '【首页，游戏，动画，鬼畜，生活，娱乐】板块都下载完成！'



@app.route('/zuiyou',methods=['GET','POST'])
def zuiyou():
    print('开始下载')
    page=request.args.get('page',10)
    url='https://www.izuiyou.com/'

    options = webdriver.ChromeOptions()  # 创建一个选项 最终运行按照选项执行
    options.add_argument('--headless')  #隐藏浏览器
    driver = webdriver.Chrome(options=options)
    # driver.maximize_window()  # 让窗口最大化
    time.sleep(2)
    #禁用webdriver检测的脚本
    script = 'Object.defineProperty(navigator, "webdriver", {get: () => false,});'
    driver.execute_script(script)
    driver.get(url)
    time.sleep(3)
    # 拉到浏览器底部
    # 拉到浏览器底部
    for _ in range(int(page)):
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(2)

    page_source = driver.page_source

    # 解析源码
    html = etree.HTML(page_source)

    # 源码写入本地
    html = etree.tostring(html, encoding="utf-8").decode("utf-8")  # 转化为字符
    with open("./zuiyou.html", "w", encoding="utf-8") as f:
        f.write(page_source)
    pattern=re.split('index-module__PostItem__main__itmiM',html)[1:]

    images_list=[]
    video_list=[]
    cover_list=[]
    n=1
    for i in pattern:
        # print(i+'\n\n')
        title=re.search('<div class="index-module__xc-ellipsis__49f5I ellipsis" style="">(.*?)</div>',i)
        # print(title)
        images=re.findall('<img class="index-module__ImageList__image__o14Sm" src="(.*?)"',i)
        # print(images)
        video=re.findall('<video src="(.*?)"',i)
        # print(title,images,video)
        cover=re.findall(r'poster="([^"]+)"',i)  #封面图
        print(cover)

        if title is not None:
            title=title.group(1)
            if len(images)>0:
                ls1=[]
                for  j in images:
                    ls1.append(j)
                images_dict={str(title):str(ls1).replace('/sz/228','')}
                images_list.append(images_dict)

            if len(video)>0:
                print(video[0])
                video_dict={str(title): 'https:'+str(video[0])}
                cover_dict={str(title): str(cover[0])}
                video_list.append(video_dict)
                cover_list.append(cover_dict)
        else:
            title=f"无标题{n}"
            if len(images)>0:
                ls2 = []
                for j in images:
                    ls2.append(j)
                images_dict = {str(title): str(ls2).replace('/sz/228', '')}
                images_list.append(images_dict)
            if len(video)>0:
                print(video[0])
                video_dict={str(title): 'https: '+str(video[0])}
                cover_dict = {str(title): str(cover[0])}
                video_list.append(video_dict)
                cover_list.append(cover_dict)
        n+=1
    list1,list2,list3=[],[],[]
    for i in images_list:
        if i not in list1:
            list1.append(i)
    for j in video_list:
        if j not in list2:
            list2.append(j)
    for k in cover_list:
        if k not in list3:
            list3.append(k)
    print(list3)

    list1=[json.dumps(i,ensure_ascii=False) for i in list1]
    list2=[json.dumps(i,ensure_ascii=False) for  i in list2]
    list3=[json.dumps(i,ensure_ascii=False) for  i in list3]
    list1=[json.loads(str(i)) for i in list1 ]  #json格式化
    list2=[json.loads(str(j)) for  j in list2 ]
    list3=[json.loads(str(k)) for  k in list3 ]


    print(list1,'\n',list2,'\n',list3)
    print(type(list1),type(list2),type(list3))
    file_path = f'D:\MP4\\{datetime.datetime.today().strftime("%Y-%m-%d")}'
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    with  open(f"{file_path}\zuiyou.txt", "w", encoding="utf-8") as f:
        f.write("图片列表:\n")
        for i in list1:
            f.write(str(i)+'\n')
    # with  open(f"{file_path}\zuiyou.txt", "a", encoding="utf-8") as f:
    #     f.write("视频列表:\n")
    #     for j in list2:
    #         f.write(str(j)+'\n')
    # with  open(f"{file_path}\zuiyou.txt", "a", encoding="utf-8") as f:
    #     f.write("封面列表:\n")
    #     for k in list3:
    #         f.write(str(k)+'\n')
    list = [{"images": list1, "video": list2, "cover": list3}]

    # 下载最右的图片
    for y in list1:
        print('开始下载图片')
        imgpath = os.path.join(f"{file_path}", "images")
        print('imgpath:', imgpath)
        if not os.path.exists(imgpath):
            os.mkdir(imgpath)
        try:
            for k2, v2 in y.items():
                title1 = k2
                url1 = v2
                urllist=url1.replace("'",'').replace('[','').replace(']','').split(',')
                print('urllist',urllist)
                n=1
                for i in urllist:
                    with open(f"{imgpath}\{title1}{str(n)}.jpg", "wb") as f:
                        f.write(requests.get(i).content)
                        print(f"{title1}{str(n)}.jpg下载完成")
                        n+=1

        except:
            print("下载失败")
            pass

    #下载最右的视频
    for x in list2:
        try:
            for k, v in x.items():
                title = k
                url = v
            #判断文件是否存在
                if os.path.exists(f"{file_path}\{title}.mp4"):
                    print(f"{title}.mp4已存在")
                else:
                    with open(f"{file_path}\{title}.mp4", "wb") as f:
                        f.write(requests.get(url).content)
                        f.close()
                        print(f"{title}.mp4下载完成")
        except:
            print("下载失败")
            pass
    #下载最右的封面
    for z in list3:
        coverpath=os.path.join(f"{file_path}","coverimg")
        print('coverpath:',coverpath)
        if not os.path.exists(coverpath):
            os.mkdir(coverpath)
        try:
            for k1, v1 in z.items():
                title1 = k1
                url1 = v1
            #判断文件是否存在
                if os.path.exists(f"{coverpath}\{title1}.jpg"):
                    print(f"{title1}.jpg已存在")
                else:
                    with open(f"{coverpath}\{title1}.jpg", "wb") as f:
                        f.write(requests.get(url1).content)
                        f.close()
                        print(f"{title1}.jpg下载完成")
        except:
            print("下载失败")
            pass
    print(type(list),list)
    print("写入完成")
    return list

@app.route('/duanzi', methods=['GET', 'POST'])
def duanzi():
    print('开始下载')
    number=request.args.get('n',30)
    url='https://www.yduanzi.com/'
    options = webdriver.ChromeOptions()  # 创建一个选项 最终运行按照选项执行
    options.add_argument('--headless')  # 隐藏浏览器
    driver = webdriver.Chrome(options=options)
    # 禁用webdriver检测的脚本
    script = 'Object.defineProperty(navigator, "webdriver", {get: () => false,});'
    driver.execute_script(script)
    driver.get(url)
    time.sleep(2)
    n=1
    file_path = f'D:\MP4\{datetime.datetime.today().strftime("%Y-%m-%d")}'
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    with open(f'{file_path}\云段子.txt', "w", encoding="utf-8") as f:
        f.write("段子列表:\n")
        while n<=int(number):
            text=driver.find_element(By.XPATH,'//*[@id="duanzi-text"]').text
            f.write(str(n)+". "+str(text).replace("\n", '')+'\n')
            print(text)
            driver.find_element(By.XPATH,'//*[@id="next-btn"]').click()
            time.sleep(1)
            n+=1
    driver.quit()
    return f"{n}个段子写入完成"

# @app.route('/youxia', methods=['GET', 'POST'])
# def youxia():
#     url=request.args.get('url','https://www.ali213.net/')
#     options = webdriver.ChromeOptions()  # 创建一个选项 最终运行按照选项执行
#     # options.add_argument('--headless')  # 隐藏浏览器
#     driver = webdriver.Chrome(options=options)
#     # 禁用webdriver检测的脚本
#     script = 'Object.defineProperty(navigator, "webdriver", {get: () => false,});'
#     driver.execute_script(script)
#     driver.get(url)
#     page_height = driver.execute_script("return document.body.scrollHeight")  # 获取高度
#     current_height = 0
#     while current_height < page_height:
#         driver.execute_script("window.scrollTo(0, arguments[0]);", current_height)
#         time.sleep(1)  # 可以根据需要调整滚动速度
#         current_height += 500
#     time.sleep(3)
#     with open("./youxia.html", "w", encoding="utf-8") as f:
#         f.write(driver.page_source)
#
#     title=driver.find_element(By.CLASS_NAME,'//*[@class="newstit"]').text
#     print(title)
#     content=driver.find_element(By.ID,'//*[@id="Content"]').text
#     print("content:",content)
#     for i in content:
#         print(i)

@app.route('/youyanshe', methods=['GET', 'POST'])
def youyanshe():
    print('开始下载')
    url = 'https://space.bilibili.com/31700507/video'
    options = webdriver.ChromeOptions()  # 创建一个选项 最终运行按照选项执行
    userAgent = UserAgent().random
    options.add_argument(f'user-agent={userAgent}')
    options.add_argument('--headless')  # 隐藏浏览器
    driver = webdriver.Chrome(options=options)
    # 禁用webdriver检测的脚本
    script = 'Object.defineProperty(navigator, "webdriver", {get: () => false,});'
    driver.execute_script(script)
    # 等待10s
    driver.get(url)
    time.sleep(2)
    # driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")  # 直接拉到浏览器底部
    # time.sleep(1)
    n = 1
    for i in range(1, 31):
        try:
            title=driver.find_element(By.XPATH, f'/html/body/div[2]/div[4]/div/div/div[2]/div[4]/div/div/ul[2]/li[{n}]/a[2]').text
            print(title)
            vedio=driver.find_element(By.XPATH,f'/html/body/div[2]/div[4]/div/div/div[2]/div[4]/div/div/ul[2]/li[{n}]/a[2]').get_attribute('href')
            print(vedio)
            cover=driver.find_element(By.XPATH, f'/html/body/div[2]/div[4]/div/div/div[2]/div[4]/div/div/ul[2]/li[{n}]/a[1]/div[1]/picture/img').get_attribute('src')
            cover=cover.split('@')[0]  #获得高清图片
            print(cover)
            #判断视频信息
            info = vedio_time(vedio)
            print(info)
            if len(info[0]) > 5 or int(info[1]) > 20:
                print(f'{info[0]}超时,不做下载')
                n+=1

            else:
                print(f'{info[0]}时长符合,开始下载')
                file_path = f'D:\MP4\\{datetime.datetime.today().strftime("%Y-%m-%d")}'
                if not os.path.exists(file_path):
                    os.mkdir(file_path)
                coverpath = os.path.join(f"{file_path}", "coverimg")
                if not os.path.exists(coverpath):
                    os.mkdir(coverpath)
                with open(os.path.join(coverpath, f"{title}.jpg"), "wb") as f:
                    f.write(requests.get(cover).content)

                os.chdir('D:\BBDown-1.6.1\BBDown-1.6.1\Binary')
                os.system(f'BBDown -tv --work-dir {file_path} {vedio}')
                n += 1
        except:
            print('下载失败,跳过')
            n += 1
            continue
        print('下载完成')
    driver.quit()
    return '下载完成'

@app.route('/A9VG',methods=['GET','POST'])
def A9VG():
    print('开始下载')
    n=request.args.get('page', 1)
    for m in range(1,int(n)+1):
        url=f'https://space.bilibili.com/19432127/video?tid=0&pn={m}'
        options = webdriver.ChromeOptions()  # 创建一个选项 最终运行按照选项执行
        userAgent = UserAgent().random
        options.add_argument(f'user-agent={userAgent}')
        options.add_argument('--headless')  # 隐藏浏览器
        driver = webdriver.Chrome(options=options)
        # 禁用webdriver检测的脚本
        script = 'Object.defineProperty(navigator, "webdriver", {get: () => false,});'
        driver.execute_script(script)
        # 等待10s
        driver.get(url)
        time.sleep(2)
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")  # 直接拉到浏览器底部
        time.sleep(1)
        x = 1
        for i in range(1, 31):
            try:
                title=driver.find_element(By.XPATH, f'/html/body/div[2]/div[4]/div/div/div[2]/div[4]/div/div/ul[2]/li[{x}]/a[2]').text
                print(title)
                vedio=driver.find_element(By.XPATH,f'/html/body/div[2]/div[4]/div/div/div[2]/div[4]/div/div/ul[2]/li[{x}]/a[2]').get_attribute('href')
                print(vedio)
                cover=driver.find_element(By.XPATH, f'/html/body/div[2]/div[4]/div/div/div[2]/div[4]/div/div/ul[2]/li[{x}]/a[1]/div[1]/picture/img').get_attribute('src')
                cover=cover.split('@')[0]
                print(cover)

                #判断视频信息
                info = vedio_time(vedio)
                print(info)
                if len(info[0]) > 5 or int(info[1]) > 20:
                    print(f'{info[0]}超时,不做下载')
                    x+=1

                else:
                    print(f'{info[0]}时长符合,开始下载')
                    file_path = f'D:\MP4\\{datetime.datetime.today().strftime("%Y-%m-%d")}'
                    cover_path=os.path.join(file_path,'coverimg')
                    if not os.path.exists(file_path):
                        os.mkdir(file_path)

                    with  open(os.path.join(cover_path,f'{title}.jpg'), 'wb') as f:
                        f.write(requests.get(cover).content)

                    os.chdir('D:\BBDown-1.6.1\BBDown-1.6.1\Binary')
                    os.system(f'BBDown -tv --work-dir {file_path} {vedio}')
                    x += 1
            except:
                print('下载失败,跳过')
                x += 1
                pass
        driver.quit()
    return '下载完成'


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    print('开始上传到数据库')
    upload_date=request.args.get('date',datetime.datetime.today().strftime("%Y-%m-%d"))
    file_path = f'D:\MP4\\{upload_date}'
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    #获取token
    # url = "http://192.168.1.1:9090/move/user/accountLogin"
    # payload = json.dumps({
    #     "userAccount": "18077133521",
    #     "userPassword": "q12345"
    # })
    # headers = {
    #     'Content-Type': 'application/json'
    # }
    #
    # response = requests.request("POST", url, headers=headers, data=payload).text
    # print(type(response), response)
    # token = json.loads(response)['data']['token']
    # print(token)

    #上传列表视频
    vedio_num=0
    file_path = f'D:\MP4\\{upload_date}'
    filelist = os.listdir(file_path)
    cover_list = os.listdir(os.path.join(file_path, 'coverimg'))
    for i in cover_list:
        for j in filelist:
            file_size = int(int(os.stat(os.path.join(f'D:\MP4\\{upload_date}',j)).st_size) / 1024 / 1024)
            if file_size<=200:
                # print('视频大小：',file_size)
                if i.split('.')[0] == j.split('.')[0]:
                    # path = f"http://127.0.0.1/download/{datetime.datetime.today().strftime('%Y-%m-%d')}/coverimg/{i}"
                    upload_path = 'http://192.168.1.1:9090/posts-resource/batchAdd'
                    data = {
                        "postsResourceList": [
                            {
                                "content": j.replace('.mp4', ''),
                                "createTime": "",
                                "id": "",
                                "isDel": 1,
                                "overview": "",
                                "picture": "",
                                "title": "",
                                "video": f"http://192.168.5.145/download/{upload_date}/{j}",
                                "videoCoverImgUrl": f"http://192.168.5.145/download/{upload_date}/coverimg/{i}"
                            }
                        ]
                    }
                    headers = {
                        'token': "xxxxxxxxxxxxxxxxxxxxxxxx",
                        "Content-Type": "application/json"}
                    r = requests.post(upload_path, data=json.dumps(data), headers=headers)
                    print(r.text)
                    print(data)
                    print('视频上传完成')
                    vedio_num+=1
    print(f'总计：{vedio_num}个视频上传完成')

    #上传段子
    try:
        if os.path.exists(f'{file_path}\云段子.txt'):
            with  open(f'{file_path}\云段子.txt', 'r', encoding='utf-8') as f:
                for i in f.readlines():
                    j = i.replace('\n', '').replace(' ', '').replace("'", '')
                    upload_path = 'http://192.168.1.1:9090/posts-resource/batchAdd'
                    data = {
                        "postsResourceList": [
                            {
                                "content": j,
                                "createTime": "",
                                "id": "",
                                "isDel": 1,
                                "overview": "",
                                "picture": "",
                                "title": "",
                                "video": "",
                                "videoCoverImgUrl": ""
                            }
                        ]
                    }
                    headers = {
                        'token': "xxxxxxxxxxxxxxxxx",
                        "Content-Type": "application/json"}
                    r = requests.post(upload_path, data=json.dumps(data), headers=headers)
                    print(data)
                    print('段子上传完成')
        else:
            print('云段子不存在')
    except:
        pass

            # else:
            #     upload_path = 'http://192.168.1.1:9090/party/posts-resource/batchAdd'
            #     data = {
            #         "postsResourceList": [
            #             {
            #                 "content": "",
            #                 "createTime": "",
            #                 "id": "",
            #                 "isDel": 0,
            #                 "overview": "",
            #                 "picture": "",
            #                 "title": i.replace('.mp4',''),
            #                 "video": f"http://127.0.0.1/download/{datetime.datetime.today().strftime('%Y-%m-%d')}/{i}",
            #                 "videoCoverImgUrl": ""
            #             }
            #         ]
            #     }
            #     headers = {
            #         "Content-Type": "application/json"}
            #     print('video',json.dumps(data))
            #     r = requests.post(upload_path, data=json.dumps(data), headers=headers)
            #     print(r.text)


    #上传最有图片
    file_path = f'D:\MP4\\{upload_date}'
    imgpath=f"{file_path}\images"
    if not os.path.exists(f"{file_path}\images"):
        os.mkdir(f"{file_path}\images")

    imglist=os.listdir(imgpath)

    try:
        dict = {}
        print('开始上传图片')
        #取出列表里的
        for x in imglist:
            name = x.split('.jpg')[0][:-1]
            if name in dict:
                dict[name].append(x)
            else:
                dict[name] = [x]
        for k, v in dict.items():
            s = ''
            for z in v:
                url = f"http://192.168.5.145/download/{upload_date}/images/{z}" + ','
                s += url
            s = s[:-1]
            upload_path = 'http://192.168.1.1:9090/posts-resource/batchAdd'
            data = {
                "postsResourceList": [
                    {
                        "content": s.split(',')[0].split('/')[-1].replace('.jpg','')[:-1],
                        "createTime": "",
                        "id": "",
                        "isDel": 1,
                        "overview": "",
                        "picture": s,
                        "title": "",
                        "video": "",
                        "videoCoverImgUrl": ""
                    }
                ]
            }
            headers = {
                'token': "xxxxxxxxxxxxxxxxxxx",
                "Content-Type": "application/json"}
            r = requests.post(upload_path, data=json.dumps(data), headers=headers)
            print(r.text)
            print(data)
            print('图片上传成功')
    except:
        print('图片上传失败')
        pass


    # #上传封面图片
    # cover_path = f'D:\MP4\\{datetime.datetime.today().strftime("%Y-%m-%d")}\coverimg'
    # cover_files = os.listdir(cover_path)
    # print(cover_files)
    # for cover in cover_files:
    #     print(cover)
    #     cover_name=cover.strip().replace("'","").replace('"','')
    #     try:
    #         upload_path = 'http://192.168.1.1:9090/party/posts-resource/batchAdd'
    #         data = {
    #             "postsResourceList": [
    #                 {
    #                     "content": "",
    #                     "createTime": "",
    #                     "id": "",
    #                     "isDel": 0,
    #                     "overview": "",
    #                     "picture": "",
    #                     "title": f"{cover_name}",
    #                     "video": "",
    #                     "videoCoverImgUrl": "http://127.0.0.1/download/" + f"{datetime.datetime.today().strftime('%Y-%m-%d')}/coverimg/{cover_name}.jpg"
    #                 }
    #             ]
    #         }
    #         headers = {
    #             "Content-Type": "application/json"}
    #         r = requests.post(upload_path, data=json.dumps(data), headers=headers)
    #         print(r.text)
    #     except:
    #         pass
        # else:
        #     for y in zuiyou[x+1:]:    #从出现视频列表的后面开始截取
        #         title = y.split(':', 1)[0].strip("{'")
        #         print(title)
        #         url = y.split(':', 1)[1].replace('"', '').replace('}', '').replace('[', '').replace(']', '').replace('\n', '')
        #         print(url)
        #
        #         upload_path = 'http://192.168.5.13:9092/party/posts-resource/batchAdd'
        #         data = {
        #             "postsResourceList": [
        #                 {
        #                     "content": "",
        #                     "createTime": "",
        #                     "id": n,
        #                     "isDel": 0,
        #                     "overview": "",
        #                     "picture": "",
        #                     "title": f"{title}",
        #                     "video": "http://127.0.0.1/download/" + f"{datetime.datetime.today().strftime('%Y-%m-%d')}/{url}",
        #                     "videoCoverImgUrl": ""
        #                 }
        #             ]
        #         }
        #         headers = {
        #             "Content-Type": "application/json"}
        #         r = requests.post(upload_path, data=json.dumps(data), headers=headers)
        #         n += 1
        #         print(r.text)

    return ['成功上传到数据库']

@app.route('/refuse', methods=['GET', 'POST'])
def refuse_list():
    select_date=request.args.get('date',datetime.datetime.today().strftime("%Y-%m-%d"))
    file_path = f'D:\MP4\\{select_date}'
    if not os.path.exists(file_path):
        return f"{select_date} 没有获取数据！"

    # 写入到HTML中
    head = f"""<!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <title>视频列表</title>
        </head>
        <body>
          <h1>【{select_date}】-视频列表</h1>
           <ul>"""

    with open('D:\\nginx-1.25.2\html\index.html', 'w', encoding='utf-8') as f:
        f.write(head)
        file_list = os.listdir(file_path)
        print(file_list)
        for file in file_list:
            #判断是否为文件
            file_is = os.path.join(file_path, file)
            if os.path.isfile(file_is):
                # 获取文件属性
                file_info = os.stat(os.path.join(file_path, file))
                file_time=file_info.st_mtime
                file_size = file_info.st_size
                print(file_info, file_size)
                f.write(
                    f'  <li><a target="_blank"; style="margin-right:100px;width:30%;text-overflow:clip;white-space: nowrap;overflow: hidden;text-overflow: ellipsis;display:inline-block;" href="http://192.168.5.145/download/{select_date}/{file}">{file} </a>   <span style="width:100px;text-align:left;display:inline-block;">{int(int(file_size)/1024/1024)}M</span> <span style="width:150px;text-align:left;display:inline-block;">{datetime.datetime.fromtimestamp(file_time).strftime("%Y-%m-%d")}</span>          </li>\n')
        f.write('</ul>')
        f.write('</body>')
        f.write('</html>')

    return f'{select_date}:页面更新成功！'

#重命名主要是排除开头带#，？等特殊符号的名字，防止url识别有问题
@app.route('/rename', methods=['POST', 'GET'])
def rename():
    rename_date=request.args.get('date',f'{datetime.datetime.today().strftime("%Y-%m-%d")}')
    file_path=f'D:\MP4\\{rename_date}'
    if not  os.path.exists(file_path):
        return {'msg':f'{file_path}文件夹不存在'}
    file_list = os.listdir(file_path)

    cover_path=os.path.join(file_path, 'coverimg')
    cover_list=os.listdir(cover_path)

    img_path=os.path.join(file_path,'images')
    img_list=os.listdir(img_path)
    ls=[]
    for file in file_list:
        if file[0] in ['#','？']:
            new_file='【'+file.split('.mp4')[0]+'】'+'.mp4'
            ls.append([file,new_file])
            os.rename(os.path.join(file_path, file),  os.path.join(file_path, new_file))
    for cover_name in cover_list:
        if cover_name[0] in ['#','？']:
            new_img='【'+cover_name.split('.jpg')[0]+'】'+'.jpg'
            ls.append([cover_name,new_img])
            os.rename(os.path.join(cover_path, cover_name),  os.path.join(cover_path, new_img))
    for img_name in img_list:
        print(img_name)
        if img_name[0] in ['#','？']:
            new_img='【'+img_name.split('.jpg')[0]+'】'+'.jpg'
            ls.append([img_name,new_img])
            os.rename(os.path.join(img_path, img_name),  os.path.join(img_path, new_img))
    with open(os.path.join(file_path, 'zuiyou.txt'), 'r', encoding='utf-8') as f:
        img_dict=f.readlines()

    with open(os.path.join(file_path, 'zuiyou.txt'), 'w', encoding='utf-8') as f:
        for img_name in img_dict:
            if img_name.strip().replace("'", '').replace('{', '')[0] in ['#', '？']:
                new_img='{'+"'"+'【'+img_name.split(':',1)[0].replace("'",'').replace('{','')+'】'+"'"+':'+img_name.split(':',1)[1]
                f.write(new_img)
                ls.append([img_name,new_img])
            else:
                f.write(img_name)
    print('重名成功列表：',ls)


    return f'{datetime.datetime.today().strftime("%Y-%m-%d")}:{ls}重命名成功！'

if __name__ == '__main__':
    # if not os.path.exists('D:/MP4'):
    #     os.mkdir('D:/MP4')
    # os.chdir('D:/nginx-1.25.2')
    # os.system('start nginx.exe')
    # print('启动nginx服务')
    app.run(host='0.0.0.0', port=9966, debug=True)
