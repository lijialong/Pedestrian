"""  
作者:Leif
time_version_1.0:2018/9/19
time_version_2.0:2018/9/22
version:2.1
引用 @维吉尔：spocLogin() courseChoose() 两个方法
感谢:@维吉尔，@坑坑, @神奇·瀚 的帮助

说明：在version1.0基础上进行了优化，使其能自动获取要刷视频的fileid，提升了效率
2.1说明：修复了部分bug
"""
import random
import re
import time
import urllib
from urllib.parse import parse_qsl, urlparse

import cv2
import requests
from PIL import Image
from pytesseract import image_to_string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class VideoPlay(object):
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.video_list = []
        self.username = '41601134'#input('请输入学号：')
        self.password = '817523'#input('请输入密码：')
        self.request_headers = {}
        self.tp = []
        self.coursech = input('请输入你想要刷的课程：')
        

    def spocLogin(self):#引用自@维吉尔
        url = 'https://spoc.tfswufe.edu.cn/'
        self.driver.delete_all_cookies() #打开浏览器时清除所有cookie
        self.driver.get(url)
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        
        uname = self.username
        pwd = self.password
        # self.username = '41603739'#input('请输入学号：')
        # self.password = '926122'#input('请输入密码：')

        self.driver.find_element_by_id('username').send_keys(uname)
        self.driver.find_element_by_id('password').send_keys(pwd)
        time.sleep(2)
        # 验证码自动识别功能，感谢@神奇·瀚
        # 保存截屏
        self.driver.save_screenshot(r'D:\\01.png')
        ran = Image.open(r"D:\\01.png")
        box = (986, 414, 1145, 474)#不同电脑的位置参数不同
        #box = (743, 390, 871, 438)#实验楼远程
        #box = (824,388,949,437)
        ran.crop(box).save(r"D:\\captcha.png")

        # 图像识别
        image = Image.open(r"D:\\captcha.png")
        text = image_to_string(image)
        #print("验证码：" + text)
        authcode = text
        self.driver.find_element_by_id('authcode').send_keys(authcode)

        self.driver.find_element_by_xpath("//input[@value='登录']").click()
        #print(self.driver.current_url)
        time.sleep(2)

        if self.driver.current_url == url:
            print('登录成功')
        else:
            print('登录失败，请重试')
            # self.username=[]
            # self.password=[]
            self.spocLogin()
        cookies = self.driver.get_cookie('ASP.NET_SessionId') #截获登录之后浏览器保存的cookies
        cookie = cookies['value'] #抓取value键的值，后期post请求需要
        # print(self.cookies)
        self.request_headers = {
                                'Host':'spoc.tfswufe.edu.cn',
                                'Origin':'https://spoc.tfswufe.edu.cn',
                                'Referer':'https://spoc.tfswufe.edu.cn/JiaoXue/CourseKnowledgePoint/StudentKnowledgePointIndex?courseId=10405&classId=69000',
                                'Connection': "keep-alive",
                                'Upgrade-Insecure-Requests':'1',
                                'Content-Type': "application/x-www-form-urlencoded",
                                'Cookie': "ASP.NET_SessionId="+str(cookie)+"; user_login_account=user_login_account="+str(self.username),
                                'X-Requested-With': "XMLHttpRequest",
                                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0",
                                }

        # print(self.request_headers['Cookie'])


    def courseChoose(self):#引用自@维吉尔，Leif进行了修改

        try:
            course = self.coursech#'E'#input('请输入你想要刷的课程：')
            courseUrl = self.driver.find_element_by_xpath("//a[contains(@title,'%s')]"%course).get_attribute('data-2') #通过xpath模糊查找到输入课程名所对应的url
            self.driver.get('https://spoc.tfswufe.edu.cn'+courseUrl)
            #print(courseUrl)
            #获取courseID
            cu = re.findall(r'\d+',courseUrl)
            #print(cu[0])
            # 获取treeid
            urltr = 'https://spoc.tfswufe.edu.cn/JiaoXue/CourseKnowledgePoint/GetKnowledgePoint?courseId='+str(cu[0])#感谢 @维吉尔 的提示
            self.driver.get(urltr)#通过get打开该页面，不能用post请求，应为获取不到任何东西
            html = self.driver.page_source#获取该页面的所有信息
            # print(html)
            # self.driver.back()
            rr = re.findall(r'\d{5}',html)#正则表达式获取长度为5的数字，即treepoint参数
            # print(rr)
            treeid = list(set(rr))#消除重复的参数
            # print(treeid)
            
            for treepoint in treeid:
                #for循环之内的方法感谢 @坑坑 同学的帮助
                page = 1
                while page <= 2:#使其能获取两页的fileid
                    url = 'https://spoc.tfswufe.edu.cn/JiaoXue/CourseKnowledgePoint/StudentGetKnowledgePointCourseware?treePoint='+treepoint+'&courseId='+str(cu[0])+'&classId='+str(cu[1])+'&pageIndex='+str(page)#2018/9/23：修复了有两页的bug
                    response = requests.get(url,headers = self.request_headers)#通过treepoint找到对应的页面
                    # print(response.text)
                    m =re.findall(r"\d{6}",response.text)#获取其中的fileid
                    m =list(set(m))#去重
                    for mpoint in m:
                        self.tp.append(mpoint)#将获取的fileid放入数组
                    if self.driver.current_url == urltr:#判断是否返回，防止返回主页导致时间刷不起
                        self.driver.back()
                    page += 1
                
                #print(m)
            # print(self.tp)
            # resp = urllib.request.urlopen(urltr) 
            # html = resp.read()
            # html.encode('utf-8')
            # print(resp.read())
            # datatr = 'courseId=10405'
            # datatr = datatr.encode('utf-8')
            # r = requests.post(urltr,data=datatr,headers=self.request_headers)
            # r.status_code
            # r.text
            # print('-'*10)
            #self.driver.back()#返回之前的页面
            print(courseUrl)
            print('已成功进入，请继续')
        except:
            print('------未找到该课程，请检查输入是否正确------')
            self.courseChoose()

    #--------用于自动获取fileID-----------
    #--------技术不足，预留代码块---------
    
    # def getVideoUrl(self):#此方法用于获取fileId

    #     try:
    #         print('')
    #     except:
    #         print('')

    
    #--------测试代码----------
    # def video(self):#进行刷视频
    #     try:
    #         int i = 1
    #         for video_lists in video_list:
    #             print('---第'+i+'个视频---')
    #             self.postvideo()
    #             i += 1
    #     except expression as e:
    #         print('---循环错误---'+str(e))


    def postvideo(self):#根据fileid刷视频
        try:
            # q = 0
            # while q == 0:#为重复获取fileId
            #     #print('111')
            #     i = input('请输入fileId:')#获取fileId
            #     i = int(i)#将i转换为整型
            #     i_len = i + 1000#刷帖区间
            #     #print('1111')
            #     while i < i_len:
            #         #print('11111')
            for i in self.tp:#根据数组中的fileid刷视频
                print(str(i))#显示当前视频的fileId
                ran = random.randint(10,150)#随机一个时间传给服务器
                url = 'https://spoc.tfswufe.edu.cn/JiaoXue/CourseKnowledgePoint/FinishedPlaying'#关闭播放的地址
                urltime = 'https://spoc.tfswufe.edu.cn/JiaoXue/CourseKnowledgePoint/PlayerRecordTime'#播放时间地址
                timerun = 'time='+str(ran)+'&fileId='+str(i)#时间post请求的data
                datatime = timerun.encode('utf-8')#utf转码
                playvideo = 'fileId='+str(i)#关闭视频页的data
                datavideo = playvideo.encode('utf-8')
                t = requests.post(urltime,data=datatime,headers=self.request_headers)#更新时间post
                r = requests.post(url,data=datavideo,headers=self.request_headers)#发送post
                print('***TimePost***'+str(t.status_code))#检测状态
                print('***PlayPost***'+str(r.status_code))#检测状态
                #     i += 1
                # if_exit = input('是否退出（1表示是，2表示否）')
                # if if_exit == '1':#判断是否退出
                #     q = 1
        except Exception as e:
            print('********'+str(e)+'********')
if __name__ == '__main__':
    ab = VideoPlay()
    ab.spocLogin()
    ab.courseChoose()
    ab.postvideo()
