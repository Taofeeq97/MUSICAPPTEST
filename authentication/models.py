import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser

from base.constants import UserType
from base.managers import ActiveManager, UserManager
from base.models import BaseModel
from base.validators import ProfilePictureValidator


class User(BaseModel, AbstractUser):
    id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    email = models.EmailField(verbose_name="email address", unique=True)
    middle_name = models.CharField(max_length=200, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, validators=[ProfilePictureValidator.validate_all])

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    objects = UserManager()
    active_objects = ActiveManager()

    def __str__(self):
        return self.email

    @property
    def get_complete_name(self):
        first_and_middle_name = (
            self.first_name + f" {self.middle_name}"
            if self.middle_name
            else self.first_name
        )
        complete_name = "%s %s" % (first_and_middle_name, self.last_name)
        return complete_name.strip()
    
