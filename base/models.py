from django.db import models
from django.utils import timezone
from base.managers import ActiveManager


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    all_objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        abstract = True
        ordering = [
            "-created_at",
        ]

    def soft_delete(self):
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def delete(self):
        return self.soft_delete()

    def force_delete(self):
        return super().delete()