from django.conf import settings
from django.db import models
from bomiot.server.core.models import DataCoreModel

class Example(DataCoreModel):
    data = models.JSONField()

    class Meta:
        db_table = settings.BASE_DB_TABLE + '_example'
        verbose_name = settings.BASE_DB_TABLE + ' Example'
        verbose_name_plural = verbose_name
        ordering = ['-id']

