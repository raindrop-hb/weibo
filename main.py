#!/usr/bin/python3.10
# -*- coding: utf-8 -*-
# Copyright (C) 2023 , Inc. All Rights Reserved 
# @Time    : 2023/8/15 20:44
# @Author  : raindrop
# @Email   : 1580925557@qq.com
# @File    : main.py

import requests,json
from tqdm import tqdm

headers={
    "cookie":"",
    "X-Xsrf-Token":"",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Server-Version":"v2023.08.15.1"
}

def m3u8(url,name):
    url_m3u8 = url
    print("直播视频合成时间较长。。。")
    m3u8_data = requests.get(url=url_m3u8).text.split()
    for ts in tqdm(m3u8_data):
        if '.ts' in ts:
            ts_url = "http://live.video.weibocdn.com/" + ts
            ts_content = requests.get(url=ts_url).content
            with open(name+'.mp4', mode='ab') as f:
                f.write(ts_content)
    print('已经下载完成')



def main():
    url_get=input("输入主页链接：")
    uid=url_get.replace("https://weibo.com/u/","")
    page=1
    while True:
        url="https://weibo.com/ajax/statuses/mymblog?uid="+uid+"&page="+str(page)+"&feature=0"
        resp=requests.get(url,headers=headers).text.encode('gbk',errors='ignore').decode('gbk')
        resp=json.loads(resp)
        if len(resp)==1:
            print("运行结束")
            break
        else:
            for aweme in resp["data"]["list"]:
                #图片
                if aweme["pic_num"]>0:
                    for pic in aweme["pic_infos"]:
                        pic_url=aweme["pic_infos"][pic]["mw2000"]["url"]
                        header_2={
                            "Referer":"https://weibo.com/",
                            "user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                        }
                        img=requests.get(pic_url,headers=header_2).content
                        with open(pic+".jpg","wb")as f:
                            f.write(img)
                        print("下载"+pic+".jpg")
                else:
                    #视频
                    video_id=aweme["url_struct"][0]["actionlog"]["oid"]
                    if "source" not in aweme["url_struct"][0]["actionlog"]:
                        header = {
                            "Page-Referer": "/tv/show/" + video_id,
                            "Referer": "https://weibo.com/tv/show/" + video_id + "?from=old_pc_videoshow",
                            "Content-Type": "application/x-www-form-urlencoded"
                        }
                        header.update(headers)
                        del header['Server-Version']
                        quot_id = video_id.replace(":", "%3A")
                        url = "https://weibo.com/tv/api/component?page=%2Ftv%2Fshow%2F" + quot_id
                        data = {
                            "data": "{\"Component_Play_Playinfo\":{\"oid\":\"" + video_id + "\"}}"
                        }
                        print(data)
                        resp = requests.post(url, data=data, headers=header).text.encode('gbk', errors='ignore').decode('gbk')
                        resp=json.loads(resp)
                        big_video=next(iter(resp["data"]["Component_Play_Playinfo"]["urls"].keys()))
                        video_url=resp["data"]["Component_Play_Playinfo"]["urls"][big_video]
                        header_2 = {
                            "Referer": "https://weibo.com/",
                            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                        }
                        video=requests.get("https:"+video_url,headers=header_2).content
                        name=video_id.replace(":","")
                        with open(name+".mp4","wb")as f:
                            f.write(video)
                        print("下载" + name + ".mp4")
                    #直播，可能有其他，格式m3u8
                    elif aweme["url_struct"][0]["actionlog"]["source"]=="live":
                        url = "https://weibo.com/l/!/2/wblive/room/show_pc_live.json?live_id=" + video_id
                        header = {
                            "Referer": "https://weibo.com/l/wblive/p/show/" + video_id,
                            "Content-Type": "application/x-www-form-urlencoded"
                        }
                        header.update(headers)
                        del header['Server-Version']
                        resp=requests.get(url,headers=header).text.encode('gbk',errors='ignore').decode('gbk')
                        resp=json.loads(resp)
                        video_url=resp["data"]["replay_origin_url"]
                        name = video_id.replace(":", "")
                        m3u8(video_url,name)
                        print("下载" + name + ".mp4")
        page+=1
#https://weibo.com/u/3170055142

if __name__ == '__main__':
    main()
