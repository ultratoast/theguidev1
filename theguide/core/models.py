from django.db.models import *
# from django.db import transaction, models
from django.utils import timezone
import django_mysql.models
from django.contrib.auth.models import User
from django.dispatch import receiver
from mptt.models import MPTTModel, TreeForeignKey
from theguide.user.models import *
from storages.backends.s3boto3 import S3Boto3Storage

MediaNoOverwriteS3BotoStorage = lambda: S3Boto3Storage(location='uploads', file_overwrite=False)
MediaS3BotoStorage = lambda: S3Boto3Storage(location='uploads', file_overwrite=True)

class ModuleType(MPTTModel):
    name = CharField(max_length=50)
    parent = TreeForeignKey('self', on_delete=CASCADE, null=True, blank=True, related_name='children')

class Module(Model):
    author = ForeignKey(User,ondelete=PROTECT)
    title = CharField(max_length=100)
    description = TextField()
    edit_copy = OneToOneField("self", on_delete=CASCADE, null=True, blank=False, unique=True)
    supermodule = TreeForeignKey('self', on_delete=CASCADE, null=True, blank=True, related_name='submodule')
    created = DateTimeField(default=timezone.now)
    activated = DateTimeField(Blank=True)
    deleted = DateTimeField(Blank=True)
    score = IntegerField(default=0)
    show_order = IntegerField(default=1)
    geolocation = GeometryField(geography=True,blank=True)
    quantity = IntegerField(blank=True)
    units = CharField(max_length=20,blank=True)

    class Meta:
        ordering = ['-created']

class ModulesByType(Model):
    module = ForeignKey(Module,ondelete=CASCADE)
    module_type = ForeignKey(ModuleType,ondelete=CASCADE)

class ModuleParticipant(Model):
    module = ForeignKey(Module,ondelete=PROTECT)
    user = ForeignKey(User,ondelete=CASCADE)
    role = CharField(max_length=50,blank=True)
    join_date = DateTimeField(default=timezone.now)

class ModuleTimeline(Model):
    module = ForeignKey(Module,ondelete=CASCADE)
    start = DateTimeField(Blank=True)
    end = DateTimeField(Blank=True)
    completed = DateTimeField(Blank=True)

class ModuleParticipantByModuleTimeline(Model):
    module = ForeignKey(Module,ondelete=CASCADE)
    timeline = ForeignKey(ModuleTimeline,ondelete=CASCADE)
    participant = ForeignKey(ModuleParticipant,ondelete=CASCADE)

def modulefile_generate_name(instance, filename):
    if "module_files" in filename:
        return filename
    else:
        if instance.module.edit_id:
            module = instance.module.edit_id
        else:
            module = instance.module.id
        # logger.error("generating new image file name for file {0} module {1}".format(filename,module))
        timestamp = round(time.time())
        filename,ext = os.path.splitext(filename)
        filename = 'modulefile_{0}_{1}_{2}_edit{3}'.format(instance.filetype,module,timestamp,ext)
        return 'module_files/{0}'.format(filename)

class ModuleFile(Model):
    module =  ForeignKey(Module,ondelete=CASCADE)
    caption = CharField(max_length=50)
    original = FileField(upload_to=modulefile_generate_name,storage=MediaS3BotoStorage(),validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'xls', 'rtf', 'xlsx', 'jpg','jpeg', 'png','gif'])])

def moduleimg_generate_name(instance, filename):
    if "module_images" in filename:
        return filename
    else:
        if instance.module.edit_id:
            module = instance.module.edit_id
        else:
            module = instance.module.id
        timestamp = round(time.time())
        filename,ext = os.path.splitext(filename)
        filename = 'moduleimage_{0}_{1}_{2}_edit{3}'.format(module,instance.show_order,timestamp,ext)
        return 'module_images/{0}'.format(filename)

def resize_img(imginput, width, height, prefix=''):
    basename, throwaway_period, ext = os.path.basename(imginput.name).rpartition(".")
    ext = ext.lower()
    if ext != 'gif' and ext != 'png':
        ext = 'jpeg'
    im = Image.open(imginput)
    output = BytesIO()
    im.thumbnail((width, height), Image.ANTIALIAS)
    im.save(output, format=ext.upper())
    output.seek(0)
    outputcopy = ContentFile(output.getvalue())
    output.close()
    rename_to = basename
    newfield = InMemoryUploadedFile(outputcopy, 'ImageField', "%s.%s" % (rename_to, ext), "image/%s" % ext,sys.getsizeof(outputcopy), None)
    im.close()
    return newfield


class ModuleImage(ModuleFile):
    original = ImageField(upload_to=moduleimg_generate_name,storage=MediaS3BotoStorage())
    large = ImageField(null=True, upload_to='module_images/large')
    medium = ImageField(null=True, upload_to='module_images/medium')
    thumbnail = ImageField(null=True, upload_to='module_images/thumbnail')
    show_order = IntegerField(default=1)

    sizes = {
        'medium': (400, 400),
        'large': (1200, 1200),
        'thumbnail': (90, 90),
    }

    def generate_sizes(self):
        for key in self.sizes:
            try:
                setattr(self, '%s' % key,resize_img(self.original, self.sizes[key][0], self.sizes[key][1]))#, prefix=key + "_"))
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error("error generating image size {0} {1}".format(key,e))

    class Meta:
        ordering = ['module', 'show_order']

@receiver(signals.post_save, sender=ListingImage)
def make_other_sizes(sender, instance, created, **kwargs):
    if created:
        try:
            instance.generate_sizes()
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error("image size generation error {0}".format(e))
        else:
            instance.save()


@receiver(signals.post_delete, sender=ModuleFile)
def file_delete(sender, instance, **kwargs):
    instance.original.delete(False)


@receiver(signals.post_delete, sender=ModuleImage)
def img_file_delete(sender, instance, **kwargs):
    # instance.original.delete(False)
    instance.thumbnail.delete(False)
    instance.medium.delete(False)
    instance.large.delete(False)

class ModuleComment(Model):
    module = ForeignKey(Module,ondelete=CASCADE)
    title = CharField(max_length=100)
    body = TextField()
    author = ForeignKey(User,ondelete=PROTECT)
    score = IntegerField(default=0)
    created = DateTimeField(default=timezone.now)
    deleted = DateTimeField(blank=True)

class Activity_Log(models.Model):
    module_id = models.CharField(max_length=80)
    action = django_mysql.models.EnumField(choices=['Created', 'Activated', 'Deleted'], default='Created')
    action_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Activation Log"
        ordering = ['-module_id']