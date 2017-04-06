from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import ArrayField


class Blog(models.Model):
    title = models.CharField(_('Title'),
                             max_length=1000)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    body = models.TextField(_('Body'))
    tags = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    is_published = models.BooleanField(_('Is published'), default=False)

    def __str__(self):
        return self.title