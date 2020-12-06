from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework import authentication, permissions
from django.db.models.aggregates import Count
from django.http import HttpResponse  

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from.crawler import *
from .serializers import *
from .models import *



class List_Episodes(APIView):

    def get(self,request,format=None):
        f_sid = request.GET.get("sid")
        url_yh = request.GET.get("url_yh")
        if f_sid != '0':
            # data_bili = parse_section_msg_bili(f_sid)
            # data_yh = parse_section_msg_yhdm(url_yh)
            executor = ThreadPoolExecutor(max_workers=2)
            all_task = [executor.submit(parse_section_msg_bili, (f_sid)),
                        executor.submit(parse_section_msg_yhdm, (url_yh))]
            for future in as_completed(all_task):
                # if future.result()[0].get('cid'):
                if id(future) == id(all_task[0]):
                    data_bili  = future.result()
                else:
                    data_yh  = future.result()

            data = []
            for i,d in enumerate(data_yh):
                have_b = 0
                for j,b in enumerate(data_bili):
                    if d.get("title") == b.get("title"):
                        have_b = 1
                        ep = b
                        ep['url'] = d.get('url')
                        
                if not have_b:
                    ep = d
                    ep["cid"] = 0
                    ep["cover"] = ""
                    ep["long_title"] = ""
                data.append(ep)
                        
            return Response(data)
        else:
            data_yh = parse_section_msg_yhdm(url_yh)
            for i,d in enumerate(data_yh):
                d["cid"] = 0
                d["cover"] = ""
                d["long_title"] = ""
    
            return Response(data_yh)
        

        return Response(EpisodesSerializer(episodes,many=True).data)

class Search(APIView):

    def get(self,request,format=None):
        kw = request.GET.get("kw")
        self.f_list = []
        f_yh, f_bili = self.find_all(kw)
        data_yh = [FanSerializer(f).data for f in f_yh ]
        data_bili = [UnmatchedFanSerializer(f).data for f in f_bili ]
        for i,d in enumerate(data_bili):
            data_bili[i]['cover'] = "http:/" + d.get('cover')
            
        dic = {"data_yh":data_yh,"data_bili":data_bili}
        return Response(dic)
    
    def find_my_db(self,kw):

        self.f_list = Fanju.objects.filter(title_yh__contains=kw)

    def find_all(self,kw):
        executor = ThreadPoolExecutor(max_workers=2)
        all_task = [executor.submit(search_bili, (kw)),executor.submit(search_yh, (kw))]
        for future in as_completed(all_task):
            if id(future) == id(all_task[1]):
                f_yh = future.result()
            elif id(future) == id(all_task[0]):
                f_bili = future.result()
                
        return (f_yh,f_bili)
        # for i,t in enumerate(title):
        #     f = Fanju.objects.filter(title_yh=t).first()
        #     # if f.sid != ""
        #     f_ = match_fanju(t)
        #     if f_ :
        #         f.title = f_.title
        #         f.sid = f_.sid
        #         f.cover = f_.cover
        #         f.save()
        #         # f_.delete()
                
class Play(APIView):
    def get(self,request,format=None):
        cid = request.GET.get("cid")
        url_yh = request.GET.get("url_yh")
        executor = ThreadPoolExecutor(max_workers=2)
        all_task = [executor.submit(download_danmu, (cid)),
                    executor.submit(get_mp4_url, (url_yh))]
        for future in as_completed(all_task):
            if id(future) == id(all_task[1]):
                mp4_url = future.result()

class List_Fan(APIView):
    '''
    根据参数返回以匹配或者未匹配的番剧
    '''
    def get(self,request,format=None):
        matched = request.GET.get("matched")
        num = int(request.GET.get("num"))
        if matched :
            f_list = Fan.objects.filter(matched=True)[:num]
        else:
            f_list = Fan.objects.filter(matched=False)[:num]

        data = [FanSerializer(f).data for f in f_list ]

        for i,d in enumerate(data):
            data[i]['cover'] = "http:/" + d.get('cover')

        dic = {"data":data}
        return Response(dic)


class Last_Updated(APIView):
    '''
    返回YH的最新更新的番剧
    '''
    def get(self,request,format=None):
        f_list = update_fan()
        data = [FanSerializer(f).data for f in f_list ]

        for i,d in enumerate(data):
            data[i]['cover'] = "http:/" + d.get('cover')

        dic = {"data":data}
        return Response(dic)

class List_unmatch_fan(APIView):
    '''
    返回未匹配的番剧,根据搜索结果排序
    '''
    def get(self,request,format=None):
        kw = request.GET.get("kw")
        f_um = search_bili(kw)
        data = [ UnmatchedFanSerializer(f).data for f in f_um ]
        for i,d in enumerate(data):
            data[i]['cover'] = "https:/" + d.get('cover')
        dic = {"data":data}
        return Response(dic)

class Match_fan(APIView):
    '''
    POST方法,匹配Fan,{'title_yh':'','title':'','sid':'',}
    '''
    def post(self,request,format=None):
        data = request.data.copy()
        f = Fan.objects.filter(title_yh=data.get('title_yh')).first()
        if not f:
            return Response({"success":False})
        
        f.title = data.get("title")
        f.sid = data.get("sid")
        # f.cover = data.get("cover")
        f.matched = True
        f.save()

        return Response({"success":True})

class Add_tag_F(APIView):
    '''
    给番剧添加tag
    '''
    def get(self,request,format=None):
        tag_name = request.GET.get('tag')
        title_yh = request.GET.get('title_yh')
        print(title_yh)
        f = Fan.objects.filter(title_yh=title_yh).first()
        if not f:
            return Response({"success":False})
        
        tag = Tag.objects.filter(name=tag_name).first()
        if not tag:
            tag = Tag.objects.create(name=tag_name)

        f.tags.add(tag)
        f.save()

        return Response({"success":True})

class Delete_tag_F(APIView):
    '''
    给番剧删除tag
    '''
    def get(self,request,format=None):
        tag_name = request.GET.get('tag')
        title_yh = request.GET.get('title_yh')
        print(title_yh)
        f = Fan.objects.filter(title_yh=title_yh).first()
        if not f:
            return Response({"success":False})
        
        tag = Tag.objects.filter(name=tag_name).first()
        if not tag:
            return Response({"success":False})
            
        f.tags.remove(tag)
        f.save()

        return Response({"success":True})

class List_tag_F(APIView):
    '''
    根据标签返回番剧
    '''
    def get(self,request,format=None):
        tag_name = request.GET.get('tag')
        num = int(request.GET.get("num"))

        tag = Tag.objects.filter(name=tag_name).first()
        if not tag:
            return Response({"success":False})

        f_list = Fan.objects.filter(tags=tag)
        data = [FanSerializer(f).data for f in f_list ]
        for i,d in enumerate(data):
            data[i]['cover'] = "http:/" + d.get('cover')
        dic = {"data":data}
        return Response(dic)

class Get_comment(APIView):
    def get(self,request,format=None):
        cid = request.GET.get('cid')
        comment = download_danmu(cid)
        return HttpResponse(comment,content_type="text/xml")  

class Get_mp4_url(APIView):

    def get(self,request,format=None):
        yid = request.GET.get('yid')
        url_yh = f"http://www.yhdm.tv/v/{yid}.html"
        mp4_url = get_mp4_url(url_yh)
        return Response({"mp4_url":mp4_url})