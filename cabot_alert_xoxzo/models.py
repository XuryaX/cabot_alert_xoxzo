from cabot.cabotapp.alert import AlertPlugin
from cabot.cabotapp.alert import AlertPluginUserData
from requests.auth import HTTPBasicAuth
from django.db import models
from django.conf import settings
from os import environ as env
from logging import getLogger
from django.template import Context, Template
import requests


logger = getLogger(__name__)


xoxzo_template = "Service {{ service.name }} {% if service.overall_status == service.PASSING_STATUS %}is back to normal{% else %}reporting {{ service.overall_status }} status{% endif %}: {{ scheme }}://{{ host }}{% url 'service' pk=service.id %}. {% if service.overall_status != service.PASSING_STATUS %}Checks failing: {% for check in service.all_failing_checks %}{% if check.check_category == 'Jenkins check' %}{% if check.last_result.error %} {{ check.name }} ({{ check.last_result.error|safe }}) {{jenkins_api}}job/{{ check.name }}/{{ check.last_result.job_number }}/console{% else %} {{ check.name }} {{jenkins_api}}/job/{{ check.name }}/{{check.last_result.job_number}}/console {% endif %}{% else %} {{ check.name }} {% if check.last_result.error %} ({{ check.last_result.error|safe }}){% endif %}{% endif %}{% endfor %}{% endif %}"

xoxzo_update_template = '{{ service.unexpired_acknowledgement.user.email }} is working on service {{ service.name }}'


class XoxzoAlertUserData(AlertPluginUserData):
    name = "Xoxzo"
    alert_number = models.CharField(max_length=50, blank=True)


class XoxzoAlert(AlertPlugin):
    name = "Xoxzo"
    author = "Shaurya"

    '''
    Hook to send alerts. Since alert will be from a pre-recorded audio,
    no need to create a custom message
    '''
    def send_alert(self, service, users, duty_officers):
        users = self._get_user_list(service, users, duty_officers)
        user_numbers = [u.alert_number for u in XoxzoAlertUserData.objects.filter(
            user__user__in=users)]

        c = Context({
            'service': service,
            'host': settings.WWW_HTTP_HOST,
            'scheme': settings.WWW_SCHEME,
            'jenkins_api': settings.JENKINS_API,
        })
        message = Template(xoxzo_template).render(c)

        self._send_xoxzo_alert(service,user_numbers,message)

    '''
    Hook to send acknowledgement update via Text to Speech API.
    '''
    def send_alert_update(self, service, users, duty_officers):
        users = self._get_user_list(service, users, duty_officers)
        user_numbers = [u.alert_number for u in XoxzoAlertUserData.objects.filter(
            user__user__in=users)]

        c = Context({
            'service': service
        })
        message = Template(xoxzo_update_template ).render(c)

        self._send_xoxzo_alert(service,user_numbers,message)

    def _get_user_list(self,service,users,duty_officers):
        if service.overall_status == service.CRITICAL_STATUS:
            return list(duty_officers)+list(users)
        else:
            return duty_officers

    def _send_xoxzo_alert(self, service,user_numbers,message=None):
        api_sid = env.get('XOXZO_API_SID')
        api_key = env.get('XOXZO_API_KEY')
        call_origin = env.get('XOXZO_ORIGIN_NUMBER')

        url = "https://api.xoxzo.com/voice/simple/playback/"

        if not api_sid:
            logger.error(
                'API SID is not set. Please set XOXZO_API_SID in your config.')
            raise Exception(
                'API SID is not set. Please set XOXZO_API_SID in your config.')

        if not api_key:
            logger.error(
                'API KEY is not set. Please set XOXZO_API_KEY in your config.')
            raise Exception(
                'API KEY is not set. Please set XOXZO_API_KEY in your config.')

        if not call_origin:
            logger.error(
                'Origin Number is not set. Please set XOXZO_ORIGIN_NUMBER in your config.')
            raise Exception(
                'Origin Number is not set. Please set XOXZO_ORIGIN_NUMBER in your config.')

        for call_in_number in user_numbers:
            resp = requests.post(url, data={
                'caller': call_origin,
                'recipient': call_in_number,
                'tts_message': message,
                'tts_lang':'en'
            },auth=HTTPBasicAuth(api_sid, api_key))
