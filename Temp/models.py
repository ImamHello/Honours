import datetime
from django.db import models
from django.utils import timezone


class API(models.Model):
    apiTemp = models.JSONField()
    pub_date = models.DateTimeField("date published")

    def __float__(self):
        return self.apiTemp


    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class Hardware(models.Model):
    hardTemp = models.FloatField(max_length=20)
    pub_date = models.DateTimeField("date published")
    
    def __str__(self):
        return f"Hardware: {self.hardTemp}°C (Published: {self.pub_date})"
    
    def was_published_recently(self):
            return self.pub_date >= timezone.now() - datetime.timedelta(days=1)



class Postcode(models.Model):
    postcode = models.CharField(max_length=10) 
    
    def __str__(self):
        return self.postcode
