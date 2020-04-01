import json             #json库
import requests
import re               #正则表达式
import bs4              #html格式转化
import time
import os               #文件io流
import urllib3
import random

#取消警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Painter:
    def __init__(self):
        #防反爬
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
            'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
            'content-type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Cookie':''
        }
        self.se = requests.Session()
        self.cookies = ''

        self.painter_id = ''
        self.painter_name = ''


    def setCookies(self, cookies):
        self.cookies = 'PHPSESSID=' + cookies
        self.headers['Cookie'] = self.cookies

    def setPainter_id(self, painter_id):
        self.painter_id = painter_id

    def setPainter_name(self, painter_name):
        self.painter_name = painter_name
        self.setDownfile_path()

    def setDownfile_path(self):
        self.downfile_path = self.file_path + self.painter_id + '_' + self.painter_name

    def set_path_head(self, head):
        self._path = head + "/"
        if isR_18:
            self.file_path = self._path + 'PixivImage_R-18/'
        else:
            self.file_path = self._path + 'PixivImage/'
        self.imgId_path = self.file_path + 'imgId/'
        if os.path.exists(self.imgId_path) == 0:
            os.makedirs(self.imgId_path)

    def sleep(self):
        time.sleep(random.uniform(1.0, 2.0))  # 随机睡眠  [1,2)

    #
    def login(self):
        login_url = 'https://www.pixiv.net/'
        try:
            self.sleep()
            self.se.post(url=login_url, headers=self.headers, timeout=15)
            print("登陆成功")
            return True
        except Exception as e:
            print("登陆失败")
            return False

    #
    def getPainter_name(self):
        homepage_url = 'https://www.pixiv.net/users/{}'.format(self.painter_id)
        headers = self.headers.copy()
        headers['Referer'] = homepage_url
        print("正在获取画师名字！")
        while (1):
            try:
                self.sleep()
                html_name = self.se.get(homepage_url, headers=headers,timeout=15)
            except Exception as e:
                print("获取失败！" + str(Re_start_time) + "s后为你重新请求！")
                time.sleep(Re_start_time)
                continue
            else:
                data = html_name.content.decode('utf-8')
                # RE刑法伺候
                name = re.findall('(?<=<title>)(.*?)(?=</title>)', data)[0]
                name = name.split(' ')[0]
                painter_name = re.sub(r'[\/:*?"<>|]', '', name)
                if painter_name == '':
                    painter_name = '无名画师'
                print("画师：" + painter_name)
                self.setPainter_name(painter_name)
                return

    #
    def getPainter_all_imgId(self):
        homepage_url = 'https://www.pixiv.net/users/{}'.format(self.painter_id)
        homepage_ajax_url = 'https://www.pixiv.net/ajax/user/{}/profile/all'.format(self.painter_id)
        headers = self.headers.copy()
        headers['Referer'] = homepage_url
        print("正在请求获取画师的所有作品Id！")
        while (1):
            try:
                self.sleep()
                html_id = self.se.get(homepage_ajax_url, headers=headers, timeout=15)
                print("获取成功！")
            except Exception as e:
                print("获取失败！" + str(Re_start_time) + "s后为你重新请求！")
                time.sleep(Re_start_time)
                continue
            else:
                ajax_json = json.loads(html_id.text)
                ajax_illusts = ajax_json["body"]["illusts"]
                ajax_manga = ajax_json["body"]["manga"]  # 用户中还存在漫画（manga）,并不是用户都有

                if len(ajax_illusts) != 0:
                    total_data_illusts = list(dict(ajax_illusts).keys())
                    for id in total_data_illusts:
                        self.getImg(id)

                if len(ajax_manga) != 0:
                    total_data_manga = list(dict(**ajax_manga).keys())
                    for id in total_data_manga:
                        self.getImg(id)
                return

    #
    def getPainter_allR_18_imgId(self):
        homepage_R_18_url = 'https://www.pixiv.net/users/{}/artworks/R-18'.format(self.painter_id)
        homepage_R_18_ajax_url = 'https://www.pixiv.net/ajax/user/{}/illustmanga/tag?tag=R-18&offset=0&limit=48'.format(
            self.painter_id)
        headers = self.headers.copy()
        headers['Referer'] = homepage_R_18_url
        print("正在请求获取画师的所有R-18作品Id！")
        while (1):
            try:
                self.sleep()
                html_id = self.se.get(homepage_R_18_ajax_url, headers=headers, timeout=15)
                print("获取成功！")
            except Exception as e:
                print("获取失败！" + str(Re_start_time) + "s后为你重新请求！")
                time.sleep(Re_start_time)
                continue
            else:
                ajax_json = json.loads(html_id.text)
                ajax_illustId = ajax_json["body"]["works"]
                for i in ajax_illustId:
                    self.getImg(i['illustId'])
                return

    #
    def isPossess(self, txt):
        if os.path.exists(txt):
            print(txt + " 已存在！")
            time.sleep(1)
            return False
        return True

    #
    def getImgName(self, img_id):
        name_ajax_url = 'https://www.pixiv.net/ajax/user/{}/profile/illusts?ids[]={}&work_category=illust&is_first_page=1'.format(
            self.painter_id, img_id)
        headers = self.headers.copy()
        headers['Referer'] = 'https://www.pixiv.net/users/{}/illustrations'.format(self.painter_id)
        print("请求获取作品名字：")
        while (1):
            try:
                html = self.se.get(name_ajax_url, headers=headers,timeout=15)
                print("请求成功")
            except Exception as e:
                print("请求失败！" + str(Re_start_time) + "s后为你重新请求！")
                time.sleep(Re_start_time)
                continue
            else:
                title = html.json()['body']['works'][img_id]['illustTitle']
                title = re.sub(r'[\/:*?"<>|]', '', title)
                return title

    #
    def getImg(self, img_id):
        txt = self.imgId_path + img_id + '.txt'
        # print(txt)
        if self.isPossess(txt) == 0:
            return

        img_name = self.getImgName(img_id)

        img_url = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id={}".format(img_id)
        img_ajax_url = "https://www.pixiv.net/touch/ajax/illust/details?illust_id={}".format(img_id)

        headers = self.headers.copy()
        headers['Referer'] = img_url
        down_list = []
        print('获取原图ing -- ' + img_id)
        while (1):
            try:
                self.sleep()
                data = self.se.get(img_ajax_url, headers=headers,timeout=15)
                print("获取成功！")
            except Exception as e:
                print("获取失败！" + str(Re_start_time) + "s后为你重新请求！")
                continue
            else:
                soup = bs4.BeautifulSoup(data.text, 'html.parser')
                # json 获取原图
                try:
                    pre = json.loads(str(soup))["body"]["illust_details"]["manga_a"]
                    for i in range(len(pre)):
                        down_list.append(pre[i]["url_big"])
                except KeyError:
                    pre = json.loads(str(soup))["body"]["illust_details"]["url_big"]  # 字符串
                    down_list.append(pre)

                # 下载
                if len(down_list) == 1:
                    self.downImg(down_list[0], img_id, img_name, False)
                else:
                    for url in down_list:
                        self.downImg(url, img_id, img_name, True)
                ###########################存储下载信息#######################################
                with open(txt, 'wb') as f:
                    f.close()
                ##############################################################################
                return

    #
    def downImg(self, img_url, img_id, img_name, isMany):
        print("请求下载img")
        headers = self.headers.copy()
        headers['Referer'] = img_url
        while (1):
            try:
                self.sleep()
                se = self.se.get(img_url, headers=headers,timeout=15)
                print("请求成功，正在下载")
            except:
                print("请求失败！" + str(Re_start_time) + "s后为你重新请求！")
                time.sleep(15)
                continue
            else:
                img = se.content
                ########################################################################################
                if isMany == False:
                    img_suffix = img_url[-4:]
                    img_file = img_name + "_" + img_id + img_suffix
                    file_path = self.downfile_path
                    down_path = file_path + '/' + img_file
                else:
                    img_suffix_text = img_url[-6:]
                    img_suffix = img_suffix_text
                    if img_suffix_text[0] == 'p':
                        img_suffix = '0' + img_suffix_text[1:]
                    file_path = self.downfile_path + '/' + img_name + "_" + img_id
                    down_path = file_path + '/' + img_suffix
                #########################################################################################
                # print(file_path)
                # print(down_path)
                #
                if os.path.exists(file_path) == 0:
                    os.makedirs(file_path)
                with open(down_path, 'ab') as f:
                    f.write(img)
                    f.close()
                print(down_path + " 下载成功")
                return



    #
    def main(self, painter_ids):
        for painter_id in painter_ids:
            self.login()
            self.setPainter_id(painter_id)
            self.getPainter_name()
            if isR_18:
                self.getPainter_allR_18_imgId()
            else:
                self.getPainter_all_imgId()






Re_start_time = 15

########################r18模式设置####################################

''''''''''''''''
注意事项：（技术有限!!!!并且不建议使用selenium模拟登陆，使用selenium可能导致cookie加快变了）    <-----------------       这很重要！！！
    该程序爬图默认不开启r18模式，请看你用户设置是否显示r18作品
    如：设置显示r18作品 且下面isR_18 = False 则程序会爬取所有图片（包括R-18以及非R-18）
    建议不开启

    若想要开启r18，则需设置显示r-18作品 且isR_18设为True（！！！请在下面直接设置！！！）
    则只爬取R18作品 且放到R18文件夹里面 不予平常作品冲突

    设置页面： https://www.pixiv.net/setting_user.php

############################################################################

    为了更好的体验，这边建议 False

    若想看r18，着开启显示且下方设为 True

'''''''''''''''''

#########################################################################
isR_18 = False  # 为False时 记得去上方页面设置隐藏r18作品




if __name__ == '__main__':

    cookies = '************************************'           #你的cookies
    _path = 'e:'                                               #存储的系统盘
    # 可为列表数组
    painter_ids = ['163536']                                   #画师id



    P = Painter()
    P.setCookies(cookies)
    P.set_path_head(_path)


    P.main(painter_ids)


































