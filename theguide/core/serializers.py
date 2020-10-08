from rest_framework import serializers
from .models import *
from django.utils import timezone
from theguide.core.user.models import *

class ProfileSeriazlier(ModelSerializer):
    class Meta:
        model = Profile
        fields = [geolocation, city, state_province, country, profile_img,]

class UserSerializer(ModelSerializer):
    profile = ProfileSerializer

    class Meta:
        model = User
        fields = [username, first_name, last_name, profile,]

class ModuleParticipantSerliazer(ModelSerializer):
    user = UserSerializer

    class Meta:
        model = ModuleParticipant
        fields = [module, user, role, join_date, ]

class ModuleTimelineSerializer(ModelSerializer):

    class Meta:
        model = ModuleTimeline
        fields = [module, start, end, completed,]

class ModuleSerializer(ModelSerializer):
    user = UserSerializer

    class Meta:
        model = Module
        fields = [title, description, user, supermodule, created, activated, deleted, score, show_order, geolocation, quantity, units, moduleimage_set, modulefile_set]

class ModuleSearchSerializer(ModelSerializer):

    class Meta:
        model = Module
        fields = [title, parent, activated, deleted, score, show_order, geolocation, quantity, units]

class ModuleTypeSerializer(ModelSerializer):

    class Meta:
        model = ModuleType
        fields = [name, parent,] 