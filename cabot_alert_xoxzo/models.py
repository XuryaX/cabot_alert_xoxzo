from cabot.cabotapp.alert import AlertPlugin
from cabot.cabotapp.alert import AlertPluginUserData

from django.db import models


from os import environ as env

from logging import getLogger
logger = getLogger(__name__)



class XoxzoAlertUserData(AlertPluginUserData):
	name = "Xoxzo Check"
	favorite_bone = models.CharField(max_length=50, blank=True)

class XoxzoAlert(AlertPlugin):
    name = "Xoxzo"
    slug = "cabot_alert_xoxzo"
    author = "Shaurya"
    version = "0.0.1"
    font_icon = "fa fa-code"

    def send_alert(self, service, users, duty_officers):
        return

