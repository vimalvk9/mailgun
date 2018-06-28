from django.db import models
import datetime
# Create your models here.

class YellowUserToken(models.Model):
    """
        Parent table for the database(contains the primary key).
    """
    user = models.IntegerField()
    yellowant_token = models.CharField(max_length=100)
    yellowant_id = models.IntegerField(default=0)
    yellowant_integration_invoke_name = models.CharField(max_length=100)
    yellowant_integration_id = models.IntegerField(default=0)
    webhook_id = models.CharField(max_length=100, default="")
    webhook_last_updated = models.DateTimeField(default=datetime.datetime.utcnow)


class YellowAntRedirectState(models.Model):
    """
        Child table
    """
    user = models.IntegerField()
    state = models.CharField(max_length=512, null=False)

class MailGunUserToken(models.Model):
    """
        Child table
    """
    user_integration = models.ForeignKey(YellowUserToken, on_delete=models.CASCADE)
    accessToken = models.CharField(max_length=32768, null=False)
    webhook_id = models.CharField(max_length=100, default="")
    apikey_login_update_flag = models.BooleanField(default=False, max_length=100)
    domain_name = models.CharField(max_length=100, default="")