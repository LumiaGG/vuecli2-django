import requests
from lxml import etree
import re
import json
import jsonpath
import threading
import time
from fuzzywuzzy import fuzz

from .serializers import *
from .models import *

import django.db.utils



def get_fanju_list_bili():
    url_global = f"https://bangumi.bilibili.com/api/timeline_v2_global"
    url_cn = f"https://bangumi.bilibili.com/api/timeline_v2_cn"
    hd = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36"
    }
    print("get_fanju_list_bili   requesting")
    r_global = requests.get(url_global, headers=hd)  #
    r_cn = requests.get(url_cn, headers=hd)  #
    print("get_fanju_list_bili   requested")
    r_global.encoding = "utf-8"
    r_cn.encoding = "utf-8"
    json_dic_global = json.loads(r_global.text)
    json_dic_cn = json.loads(r_cn.text)
    name = jsonpath.jsonpath(json_dic_global, "$..title")
    sid = jsonpath.jsonpath(json_dic_global, "$..season_id")
    cover = jsonpath.jsonpath(json_dic_global, "$..cover")

    name += jsonpath.jsonpath(json_dic_cn, "$..title")
    sid += jsonpath.jsonpath(json_dic_cn, "$..season_id")
    cover += jsonpath.jsonpath(json_dic_cn, "$..cover")
    print("get_fanju_list_bili   handled")

    for i,n in enumerate(name):
        f = UnMatchedFanju.objects.filter(sid=sid[i]).first()
        if not f:
            UnMatchedFanju.objects.create(title=n,sid=sid[i],cover=cover[i])

def get_timeline_bili():
    url_global = f"https://bangumi.bilibili.com/web_api/timeline_global"
    url_cn = f"https://bangumi.bilibili.com/web_api/timeline_cn"
    hd = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36"
    }
    r_global = requests.get(url_global, headers=hd)  #
    r_cn = requests.get(url_cn, headers=hd)  #
    r_global.encoding = "utf-8"
    r_cn.encoding = "utf-8"
    json_dic_global = json.loads(r_global.text)
    json_dic_cn = json.loads(r_cn.text)

    result_global = jsonpath.jsonpath(json_dic_global, "$.result")
    result_cn = jsonpath.jsonpath(json_dic_cn, "$.result")
    result = result_global[0][6:] + result_cn[0][6:]

    for i,day in enumerate(result):
        seasons = day.get('seasons')
        date = f"{time.gmtime().tm_year}-{day.get('date')}"
        for j,sea in enumerate(seasons):
            f = Fanju.objects.filter(title=sea.get("title")).first()
            if not f:
                f_data = {
                    'title':sea.get('title'),
                    'title_yh':"",
                    "sid":sea.get("season_id"),
                    'cover':sea.get('cover'),
                    'last_episodes':sea.get('pub_index')
                }
                f = Fanju.objects.create(**f_data)
            
            data = {
                "fanju":f,
                "pub_index":sea.get("pub_index"),
                "pub_time":sea.get("pub_time"),
                "date":date
                }
            e = Episodes.objects.filter(fanju=f).first()
            if not e:
                Episodes.objects.create(**data)
            else:
                Episodes.objects.filter(id=e.pk).update(**data)

def get_fanju_update_yh():
    """

    """
    url = "http://www.yhdm.tv/"
    hd = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36"
    }
    r = requests.get(url, headers=hd)  #
    r.encoding = "utf-8"
    html = etree.HTML(r.text)
    name = html.xpath("//div[@class='img'][1]/ul//p[@class='tname']/a/text()")
    url = html.xpath("//div[@class='img'][1]/ul//p[@class='tname']/a/@href")
    cover = html.xpath("//div[@class='img'][1]/ul//a/img/@src")
    pub_index = html.xpath("//div[@class='img'][1]/ul//p[2]/a/text()")
    for i,p in enumerate(pub_index):
        cover[i] = cover[i].replace('http:','')
        pub_index[i] = p.replace('集','话')
    # title_url = html.xpath("//div[@class='img'][1]/ul//p[2]/a/@href") # 直接到番剧的播放页
    return (name,url,cover,pub_index)

def update_fan():
    '''
    返回的是YH当前最近更新的番剧列表
    '''
    title,url,cover,pub_index = get_fanju_update_yh()
    f_list = []
    UpdateUnMatchedFanju = 0
    for i,t in enumerate(title):
        f = Fan.objects.filter(title_yh=t).first()
        if f:
            f.last_episodes = pub_index[i]
            f.save()

        else:
            data = {
                'title':"", 
                'title_yh':t, 
                'url_yh':url[i], 
                'sid':0,
                'last_episodes':pub_index[i], 
                'cover':cover[i],
                'matched':False
            }
            f = Fan.objects.create(**data)

        f_list.append(f)

    return f_list

def search_yh(kw):
    url = f"http://www.yhdm.tv/search/{kw}/"
    hd = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36"
    }
    r = requests.get(url, headers=hd)  #
    r.encoding = "utf-8"
    html = etree.HTML(r.text)

    title = html.xpath("//div[@class='lpic']/ul//h2//@title")
    url = html.xpath("//div[@class='lpic']/ul//h2//@href")
    # pub_index = html.xpath("//div[@class='lpic']/ul//span[1]/font/")
    cover = html.xpath("//div[@class='lpic']/ul//a/img/@src")
    for i,c in enumerate(cover):
        cover[i] = c.replace('http:','')
    f_list = []
    for i,t in enumerate(title):
        f = Fan.objects.filter(title_yh=t).first()
        if not f:
            data = {
            'title':"", 
            'title_yh':t, 
            'url_yh':url[i], 
            'sid':0,
            'last_episodes':None, 
            'cover':cover[i],
            'matched':False,
            }
            f = Fan.objects.create(**data)
        f_list.append(f)

    return f_list

def search_bili(kw):
    url = f"https://api.bilibili.com/x/web-interface/search/type?keyword={kw}&page=1&search_type=media_bangumi&order=totalrank&pagesize=20"
    hd = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36"
    }
    r = requests.get(url,headers=hd)
    r.encoding = 'utf-8'
    json_dic = json.loads(r.text)
    result = jsonpath.jsonpath(json_dic, "$..result")
    f_um_list = []
    if result == False:
        return []
    for i,r in enumerate(result[0]):
        f_um = UnMatchedFan.objects.filter(title=r.get("title")).first()
        if not f_um:
            t = r.get('title').replace('<em class="keyword">','')
            t = t.replace('</em>','')
            data = {
                'title':t,
                'sid':r.get("season_id"),
                'cover':r.get('cover'),
            }
            f_um = UnMatchedFan.objects.create(**data)

        f_um_list.append(f_um)

    return f_um_list

def parse_section_msg_yhdm(url_yh):
    url = f"http://www.yhdm.tv{url_yh}"
    hd = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36"
    }
    r = requests.get(url, headers=hd)  #
    r.encoding = "utf-8"
    re_txt = re.findall("播放列表([\S\s]*)动漫介绍", r.text)
    title_list = re.findall('nk">(.*?)</a', re_txt[0])
    url_list = re.findall('href="(.*?)"', re_txt[0])
    data = []
    for i,t in enumerate(title_list):
        # t = "".join(re.findall("[1-9]", "".join(re.findall("第(.*?)集", t))))
        t = "".join(re.findall("第(.*?)集", t))
        if t == "":
            t = title_list[i]
        elif t[0] == '0':
            t = t[1]
        ep = {
            "title":t,
            "url":"http://www.yhdm.tv" + url_list[i],
        }
        data.append(ep)

    return data[::-1]

def parse_section_msg_bili(s_id):
    """
    返回：各集封面图，aid，cid，id(ep号)，title(剧集标题)
    """
    url = f"https://api.bilibili.com/pgc/web/season/section?season_id={s_id}"
    hd = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36"
    }
    r = requests.get(url, headers=hd)  #
    r.encoding = "utf-8"
    json_dic = json.loads(r.text)
    try:
        episodes = jsonpath.jsonpath(json_dic, "$..main_section.episodes")[0]
    except TypeError: #'bool' object is not subscriptable:
        return []
    data = []
    for i,e in enumerate(episodes):
        ep = {
            "cid":e.get("cid"),
            "cover":e.get("cover"),
            "long_title":e.get("long_title"),
            "title":e.get("title"),
        }
        data.append(ep)

    return data

def download_danmu(cid):
    if cid != "0":
        url = f"https://comment.bilibili.com/{cid}.xml"
        hd = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36"
        }
        r = requests.get(url, headers=hd)  #
        r.encoding = "utf-8"
        # with open(
        #     f"/static/xml/{cid}.xml", "w", encoding="utf-8"
        # ) as f:
        #     f.write(r.text)
        # return 1
    # return 0
        return r.text

def get_mp4_url(url):
    hd = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36"
    }
    r = requests.get(url, headers=hd)  #
    while r.headers.get("Location") != None:
        url = r.headers.get("Location")
        r = requests.head(url, headers=hd, allow_redirects=False)
    url = "".join(re.findall('data-vid="(.*?)"', r.text))
    url = url.replace("$mp4", "")
    if "http" not in url:
        url = f"http://tup.yhdm.tv/?vid={url}"
        r = requests.get(url, headers=hd)
        url = "".join(re.findall('src="(.*?)"', r.text))
        r = requests.get(url, headers=hd)
        url = "".join(re.findall('url: "(.*?)"', r.text))

    r = requests.head(url, headers=hd, allow_redirects=False)
    while r.headers.get("Location") != None:
        url = r.headers.get("Location")
        r = requests.head(url, headers=hd, allow_redirects=False)
    # url = 'http://photovideo.photo.qq.com/1075_0b5353pdkaiaemaji2i3kfpth3qegwjqaf2a.f20.mp4?dis_k=bb106ba15c493a4fed76affd9483631b&dis_t=1595659796'
    return url


#*****************************弃用**************************************
def _update_fanju():
    '''
    返回的是YH当前最近更新的番剧列表
    '''
    title,url,cover,pub_index = get_fanju_update_yh()
    f_list = []
    UpdateUnMatchedFanju = 0
    for i,t in enumerate(title):
        f = Fan.objects.filter(title_yh=t).first()
        if f:
            f.last_episodes = pub_index[i]
            f.save()
            f_list.append(f)
            continue

        if not UpdateUnMatchedFanju:
            UpdateUnMatchedFanju = 1
            get_fanju_list_bili() # 更新待匹配的番剧

        f_ = match_fanju(t)
        if not f_:
            data = {
                'title':"", 
                'title_yh':t, 
                'url_yh':url[i], 
                'sid':0,
                'last_episodes':pub_index[i], 
                'cover':cover[i]
            }
        else:
            data = {
                'title':f_.title, 
                'title_yh':t, 
                'url_yh':url[i], 
                'sid':f_.sid,
                'last_episodes':pub_index[i], 
                'cover':f_.cover
            }
            # f_.delete()

        f = Fan.objects.create(**data)
        f_list.append(f)

    # for i,f in enumerate(f_list):
    #     print(f"BI:{f.title}   YH:{f.title_yh}")
    return f_list

def _match_fanju(title): 
    '''
    将YH和bili的番剧匹配
    '''
    f_list = UnMatchedFanju.objects.all()
    # for i in range(UnMatchedFanju.objects.count()):
    for i,f in enumerate(f_list):
        match_index = fuzz.token_sort_ratio(title,f.title)
        if fuzz.token_sort_ratio(title,f.title) > 65:
            f_ = f
            if "僅限" in f.title and i < len(f_list)-2:
                # f = UnMatchedFanju.objects.get(id=i+2)
                f = f_list[i+1]
                if fuzz.token_sort_ratio(title,f.title) > 49:
                    f_ = f
            return f_
        
    return 0

def match_fanju(title): 
    def sort_key(elem):
        return elem[0]

    f_list = UnMatchedFanju.objects.all()
    match_index_list = []
    for i,f in enumerate(f_list):
        match_index = fuzz.ratio(title,f.title)
        match_index_list.append([match_index,f.pk,title,f.title])

    match_index_list.sort(key=sort_key)
    if match_index_list[-1][0] > 69:
        return UnMatchedFanju.objects.get(id=match_index_list[-1][1])
    else :
        return 0
