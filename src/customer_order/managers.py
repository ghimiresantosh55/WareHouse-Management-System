from django.db import models


class OrderDetailQueryset(models.QuerySet):
    def approved(self):
        return self.filter(cancelled=False)

class OrderDetailManager(models.Manager):
    def get_queryset(self):
        return OrderDetailQueryset(self.model, using=self._db)

    def approved(self, *args, **kwargs):

        return self.get_queryset().approved()
       
    
