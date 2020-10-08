from django.db.models import *
# from django.db import transaction, models
from django.utils import timezone
import django_mysql.models
from django.contrib.auth.models import User
from django.dispatch import receiver
# from mptt.models import MPTTModel, TreeForeignKey
from theguide.user.models import *
from storages.backends.s3boto3 import S3Boto3Storage

MediaNoOverwriteS3BotoStorage = lambda: S3Boto3Storage(location='uploads', file_overwrite=False)
MediaS3BotoStorage = lambda: S3Boto3Storage(location='uploads', file_overwrite=True)

def profileimg_generate_name(instance, filename):
    if "profile_images" in filename:
        return filename
    else:
        profile = instance.id
        timestamp = round(time.time())
        filename,ext = os.path.splitext(filename)
        filename = 'profileimage_{0}{1}'.format(profile,ext)
        return 'profile_images/{0}'.format(filename)

class Profile(Model):
    user = ForeignKey(User,ondelete=CASCADE)
    geolocation = GeometryField(geography=True,blank=True)
    # address1 = CharField(blank=True)
    # address2 = CharField(blank=True)
    city = CharField(blank=True)
    state_province = CharField(blank=True)
    country = CharField(blank=True)
    phone = CharField(blank=True)
    join_date = DateTimeField(default=timezone.now)
    profile_img = ImageField(upload_to=profileimg_generate_name,storage=MediaS3BotoStorage())