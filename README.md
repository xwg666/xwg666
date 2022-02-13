import os
import pandas as pd
import openpyxl as op
import tkinter.filedialog as fd
try:
    root=fd.Tk()      #创建一个tk实例
    root.withdraw()    #隐藏实例
    filename=fd.askopenfilename(title='选择cce导出表')

    #path='C:/Users/61717/Desktop/CCE_ARM.xlsx'
    data=pd.read_excel(filename,sheet_name=1,usecols=[2,3])  #读取Excel表中第二sheet，第三四列数据
    #print(data)

    #定义manger VRF和DMZ VRF的互联地址
    #manage=input('输入manage VRF地址：')
    #DMZ=input('输入DMZ VRF地址：')
    manage='10.190.143.1'
    DMZ='10.190.143.2'
    #提取各浮动IP地址
    class ip():
        print('在防火墙上需要配置的路由')
        def ip1(row1):
            if row1.参数key=='regionlb_lvs_alb_float_ip':
                print(f'ip route-static', row1.规划值, '255.255.255.255', manage)
        data.apply(ip1,axis=1)
        def ip2(row2):
            if row2.参数key=='podlb_lvs_adv_alb_float_ip':
                print(f'ip route-static', row2.规划值, '255.255.255.255', DMZ)
        data.apply(ip2,axis=1)
        def ip3(row3):
            if row3.参数key=='podlb_lvs_float_ip':
                print(f'ip route-static', row3.规划值, '255.255.255.255', DMZ)
        data.apply(ip3,axis=1)
        def ip4(row4):
            if row4.参数key=='reverselb_lvs_float_ip':
                print(f'ip route-static', row4.规划值, '255.255.255.255', DMZ)
        data.apply(ip4,axis=1)
    #------------------------------
    print("在交换机上需要配置的路由")
except:
    print("未选择文件")
#with open(os.path.join(os.path.expanduser('~'),'Desktop/路由表.txt'),mode='w') as f: #调用os,默认桌面路径
    #for i in ip:

