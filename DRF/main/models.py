from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=100,unique=True)


class Fan(models.Model):
    title = models.CharField(max_length=100)
    title_yh = models.CharField(max_length=100)
    url_yh = models.URLField(blank=True,null=True)
    sid = models.IntegerField()
    cover = models.ImageField(blank=True)
    cover_loc = models.ImageField(blank=True, null=True)
    last_episodes = models.CharField(max_length=100,null=True)
    summary = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, null=True)
    matched = models.BooleanField()
    created_time = models.DateTimeField(auto_now_add=True)


class UnMatchedFan(models.Model):
    title = models.CharField(max_length=100)
    sid = models.IntegerField()
    cover = models.ImageField(blank=True)