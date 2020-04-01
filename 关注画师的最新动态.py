import json
import requests
import re
import bs4
import time
import os
import urllib3
import random

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # 取消警告


# 关注画师的最新动态
class Pixiv_the_latest_works_by_Painter:
    def __init__(self):
        self.se = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
            'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
            'content-type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Cookie': ''
        }
        self.cookies = ''

        # 信息列表
        self.infor = {
            'img_id': '',
            'painter_id': '',
            'painter_name': ''
        }
        self.infor_item = []  # 存储目前页面作品id 画师名字 画师id（max=20）

        # 当前页面
        if isR_18:
            self.the_latest_works_by_Painter_url = 'https://www.pixiv.net/bookmark_new_illust_r18.php?p='
        else:
            self.the_latest_works_by_Painter_url = 'https://www.pixiv.net/bookmark_new_illust.php?p='

        #################################存储路径信息#########################################
        self._path_head = ''
        self._path = self._path_head + ':/'  # 系统盘
        if isR_18:
            self.file_path = self._path + 'PixivImage_R-18/'
        else:
            self.file_path = self._path + 'PixivImage/'
        self.imgId_path = self.file_path + 'imgId/'

    ######################################################################################
    def setCookies(self, cookies):
        self.cookies = 'PHPSESSID=' + cookies
        self.headers['Cookie'] = self.cookies

    def set_path_head(self, _path_head):
        self._path = _path_head + "/"
        if isR_18:
            self.file_path = self._path + 'PixivImage_R-18/'
        else:
            self.file_path = self._path + 'PixivImage/'
        self.imgId_path = self.file_path + 'imgId/'
        if os.path.exists(self.imgId_path) == 0:
            os.makedirs(self.imgId_path)

    #
    def sleep(self):
        time.sleep(random.uniform(1.0, 2.0))  # 随机睡眠  [1,2)

    #
    def login(self):
        login_url = 'https://www.pixiv.net/'
        try:
            self.sleep()
            self.se.post(url=login_url, headers=self.headers,timeout=15)
            print("登陆成功")
            return True
        except Exception as e:
            print("登陆失败")
            return False

    #
    def exchange_page(self, page_num):
        print("正在更新页面！")
        while (1):
            try:
                self.sleep()
                headers = self.headers.copy()
                headers['Referer'] = self.the_latest_works_by_Painter_url
                html = self.se.get(self.the_latest_works_by_Painter_url + str(page_num), headers=self.headers,timeout=15)
                print('目前页面：' + self.the_latest_works_by_Painter_url + str(page_num))
                return html
            except Exception as e:
                print("请求更新页面失败," + str(Re_start_time) + "s后为你重新请求！")
                time.sleep(Re_start_time)
                continue

    # 并不能保证100%获取到画师名字
    def getPainterName(self, Painter_id):
        headers = self.headers.copy()
        headers['Referer'] = 'https://www.pixiv.net/'
        painter_url = 'https://www.pixiv.net/users/{}'.format(Painter_id)
        print('正在获取名字ing -- By_ ' + Painter_id)
        while (1):
            try:
                self.sleep()
                se = self.se.get(painter_url, headers=self.headers,timeout=15)
            except Exception as e:
                print("获取名字失败," + str(Re_start_time) + "s后为你重新请求！")
                time.sleep(Re_start_time)
                continue
            else:
                data = se.content.decode('utf-8')
                # RE刑法伺候
                name = re.findall('(?<=<title>)(.*?)(?=</title>)', data)[0]
                # 得到的是  三湊かおり - pixiv
                name = name.split(' ')[0]
                # 去除敏感符号防止命名文件时出错
                painter_name = re.sub(r'[\/:*?"<>|]', '', name)
                se.close()
                if painter_name == '':
                    return '无名画师'
                else:
                    return painter_name

    #
    def getImgId(self, html):
        soup = bs4.BeautifulSoup(html.text, "html.parser")
        img_serch = soup.find_all("div", id="js-mount-point-latest-following")
        img_ids = re.findall(r'"illustId":"(.*?)"', str(img_serch))
        painter_names = re.findall(r'"userName":"(.*?)"', str(img_serch))
        painter_ids = re.findall(r'"userId":"(.*?)"', str(img_serch))

        for i in range(len(img_ids)):
            painter_name = painter_names[i]
            if '\\' in painter_names[i]:
                painter_name = self.getPainterName(painter_ids[i])
            infor = self.infor.copy()
            infor['img_id'] = img_ids[i]
            infor['painter_id'] = painter_ids[i]
            infor['painter_name'] = painter_name
            self.infor_item.append(infor)

    def isPossess(self, txt):
        if os.path.exists(txt):
            print(txt + " 已存在！")
            time.sleep(1)
            return False
        return True

    #
    def getImg(self, infor):
        txt = self.imgId_path + infor['img_id'] + '.txt'
        if self.isPossess(txt) == False:
            return

        img_url = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id={}".format(infor['img_id'])
        img_ajax_url = "https://www.pixiv.net/touch/ajax/illust/details?illust_id={}".format(infor['img_id'])
        headers = self.headers.copy()
        headers['Referer'] = img_url

        down_list = []
        print('获取原图ing -- ' + infor['img_id'])
        while (1):
            try:
                self.sleep()
                data = self.se.get(img_ajax_url, headers=headers, timeout=15)
                print("获取成功！")
            except Exception as e:
                print("获取原图失败," + str(Re_start_time) + "s后为你重新请求！")
                time.sleep(Re_start_time)
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
                    self.downImg(down_list[0], infor, False)
                else:
                    for url in down_list:
                        self.downImg(url, infor, True)
                ###########################存储下载信息#######################################
                with open(txt, 'wb') as f:
                    f.close()
                ###############################################################################
                return

    #
    def getImgName(self, img_id, painter_id):
        name_ajax_url = 'https://www.pixiv.net/ajax/user/{}/profile/illusts?ids[]={}&work_category=illust&is_first_page=1'.format(
            painter_id, img_id)
        headers = self.headers.copy()
        headers['Referer'] = 'https://www.pixiv.net/users/{}/illustrations'.format(painter_id)
        print("请求获取作品名字")
        while (1):
            try:
                html = self.se.get(name_ajax_url, headers=headers, timeout=15)
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
    def downImg(self, img_url, infor, isMany):

        img_name = self.getImgName(infor['img_id'], infor['painter_id'])

        print("请求下载img " + img_name)
        headers = self.headers.copy()
        headers['Referer'] = img_url
        while (1):
            try:
                self.sleep()
                se = self.se.get(img_url, headers=headers,timeout=15)
                print("下载ing")
            except:
                print("请求下载失败," + str(Re_start_time) + "s后为你重新请求！")
                time.sleep(Re_start_time)
                continue
            else:
                img = se.content
                ########################################################################################
                if isMany == False:
                    img_suffix = img_url[-4:]
                    img_file = img_name + '_' + infor['img_id'] + img_suffix
                    file_path = self.file_path + infor['painter_id'] + '_' + infor['painter_name']
                    down_path = file_path + '/' + img_file
                else:
                    img_suffix_text = img_url[-6:]
                    img_suffix = img_suffix_text
                    if img_suffix_text[0] == 'p':
                        img_suffix = '0' + img_suffix_text[1:]
                    file_path = self.file_path + infor['painter_id'] + '_' + infor[
                        'painter_name'] + '/' + img_name + '_' + infor['img_id']
                    down_path = file_path + '/' + img_suffix
                #########################################################################################
                #
                if os.path.exists(file_path) == 0:
                    os.makedirs(file_path)
                with open(down_path, 'ab') as f:
                    f.write(img)
                    f.close()
                print(down_path + " 下载成功")
                return

    #
    def main(self, start_page, end_page):
        self.login()
        end_page += 1
        for i in range(start_page, end_page, 1):
            self.infor_item.clear()
            html = self.exchange_page(i)
            self.getImgId(html)
            for infor in self.infor_item:
                self.getImg(infor)
            f = open('num.txt', 'w')
            f.write(str(i))
            f.close()



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
isR_18 = False  # 为False时 记得去上方页面设置隐藏r18作品


if __name__ == '__main__':

    cookies = '**************************'

    _path_head = 'e:'  # 系统盘

    #########################页面交互-页面区间[1,100]###############################
    start_page = 1
    end_page = 100
    #################################################################################

    #########################################################################
    P = Pixiv_the_latest_works_by_Painter()
    P.setCookies(cookies)
    P.set_path_head(_path_head)
    #
    if os.path.exists(P.imgId_path) == 0:
        os.makedirs(P.imgId_path)



    P.main(start_page, end_page)

































