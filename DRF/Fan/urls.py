from django.urls import path
from django.conf.urls import url
from main.views import *

urlpatterns = [
    url(r'^api/search$',Search.as_view()),
    url(r'^api/listepisodes$',List_Episodes.as_view()),
    url(r'^api/lastupdate$',Last_Updated.as_view()),
    url(r'^api/listunmatchfan$',List_unmatch_fan.as_view()),
    url(r'^api/listfan$',List_Fan.as_view()),
    url(r'^api/match$',Match_fan.as_view()),
    url(r'^api/addtagf$',Add_tag_F.as_view()),
    url(r'^api/deletetagf$',Delete_tag_F.as_view()),
    url(r'^api/listtagf$',List_tag_F.as_view()),
    url(r'^api/getmp4url$',Get_mp4_url.as_view()),
    url(r'^api/comment$',Get_comment.as_view()),
]
