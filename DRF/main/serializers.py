from rest_framework import serializers
from .models import *

class FanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fan
        fields = "__all__"

class UnmatchedFanSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnMatchedFan
        fields = "__all__"
