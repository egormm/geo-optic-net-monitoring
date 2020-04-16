from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models as geo_models
from django.db import models

from app.utils import int_to_bijective_hexavigesimal


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        """Create and save a new user"""
        if not email:
            raise ValueError("Empty email is restricted")
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and save a new super user"""
        user = self.create_user(email=email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that support email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Client(models.Model):
    online = models.BooleanField(default=False)
    mac = models.BigIntegerField(null=True, unique=True)
    ip = models.BigIntegerField(null=True)


class Box(geo_models.Model):
    user = geo_models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=geo_models.SET_NULL,
        null=True,
    )
    name = geo_models.TextField(blank=False, default="")
    description = geo_models.TextField(blank=True)
    type_of_box_choices = (
        ('regular', 'regular'),
        ('client', 'client')
    )
    type_of_box = geo_models.CharField(
        max_length=7,
        choices=type_of_box_choices,
        default='regular'
    )
    splitters_number = models.IntegerField(default=0)
    point = geo_models.PointField()
    client = models.OneToOneField(Client, on_delete=models.SET_NULL, null=True, related_name="connected_box")

    def __str__(self):
        return self.name


class Wire(geo_models.Model):
    user = geo_models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=geo_models.SET_NULL,
        null=True,
    )
    description = geo_models.TextField(blank=True, default="")
    start = geo_models.ForeignKey(
        Box,
        on_delete=geo_models.CASCADE,
        related_name="output_wires"
    )
    end = geo_models.ForeignKey(
        Box,
        on_delete=geo_models.CASCADE,
        related_name="input_wires"
    )
    path = geo_models.LineStringField()


class Fiber(models.Model):
    color = models.CharField(max_length=32)
    start_content_type = models.ForeignKey(ContentType,
                                           on_delete=models.CASCADE,
                                           related_name="start")
    start_object_id = models.PositiveIntegerField()
    start_object = GenericForeignKey('start_content_type', 'start_object_id')
    end_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="end")
    end_object_id = models.PositiveIntegerField()
    end_object = GenericForeignKey('end_content_type', 'end_object_id')
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name="inbox_fiber")


class InputPigTail(models.Model):
    input = models.OneToOneField(Wire, on_delete=models.CASCADE, related_name="end_pigtail")
    terminals = GenericRelation(Fiber, object_id_field='start_object_id', content_type_field='start_content_type')
    n_terminals = models.IntegerField(null=True)
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name="inbox_input")


class OutputPigTail(models.Model):
    output = models.OneToOneField(Wire, on_delete=models.CASCADE, related_name="start_pigtail")
    terminals = GenericRelation(Fiber, object_id_field='end_object_id', content_type_field='end_content_type')
    n_terminals = models.IntegerField(null=True)
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name="inbox_output")


class Splitter(models.Model):
    input = GenericRelation(Fiber, object_id_field='end_object_id', content_type_field='end_content_type')
    outputs = GenericRelation(Fiber, object_id_field='start_object_id', content_type_field='start_content_type')
    n_terminals = models.IntegerField(null=True)
    label = models.CharField(max_length=8)
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name="inbox_splitter")

    class Meta:
        unique_together = ['label', 'box']

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.label = int_to_bijective_hexavigesimal(self.box.splitters_number)
            self.box.splitters_number = self.box.splitters_number + 1
            self.box.save()
        super().save(*args, **kwargs)
