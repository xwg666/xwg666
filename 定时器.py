import datetime

import schedule
import time
import requests

def my_function():
    print(datetime.datetime.now())   #http://192.168.5.145:9966/upload
    for i in ['http://192.168.5.145:9966/duanzi','http://192.168.5.145:9966/zuiyou',
              'http://192.168.5.145:9966/A9VG','http://192.168.5.145:9966/youyanshe','http://192.168.5.145:9966/all_bili',
              'http://192.168.5.145:9966/rename','http://192.168.5.145:9966/refuse','http://192.168.5.145:9966/upload']:
            response=requests.get(i)
            if response.status_code==200:
                print(response.content.decode('utf-8'))
                print('成功')
            else:
                print('错误，paas')
                pass

    print('上传成功')
    return '执行完成'
# 定义每天早上8:00执行的任务
def scheduled_job():
    schedule.every().day.at("08:00").do(my_function)
    print('启动定时任务')
    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__ == '__main__':
    scheduled_job()
    print('程序执行完成')
