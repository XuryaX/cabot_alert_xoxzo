from cabot.cabotapp.tests.tests_basic import LocalTestCase
from mock import Mock, patch

from cabot.cabotapp.models import UserProfile, Service
from cabot_alert_xoxzo import models
from cabot.cabotapp.alert import update_alert_plugins


class TestXoxzoAlerts(LocalTestCase):

    def setUp(self):
        super(TestXoxzoAlerts, self).setUp()

        self.xoxzo_user_data = models.XoxzoAlertUserData.objects.create(
            alert_number="+919804310469",
            user=self.user.profile,
            title=models.XoxzoAlertUserData.name,
        )
        self.xoxzo_user_data.save()

        self.service.users_to_notify.add(self.user)

        update_alert_plugins()
        self.xoxzo_plugin = models.XoxzoAlert.objects.get(
            title=models.XoxzoAlert.name)
        self.service.alerts.add(self.xoxzo_plugin)
        self.service.save()
        self.service.update_status()

    def test_users_to_notify(self):
        self.assertEqual(self.service.users_to_notify.all().count(), 1)
        self.assertEqual(self.service.users_to_notify.get(
            pk=1).username, self.user.username)

    @patch('cabot_alert_xoxzo.models.XoxzoAlert._send_xoxzo_alert')
    def test_normal_alert(self, fake_xoxzo_alert):
        self.service.overall_status = Service.PASSING_STATUS
        self.service.old_overall_status = Service.ERROR_STATUS
        self.service.save()
        self.service.alert()
        fake_xoxzo_alert.assert_called_with(self.service,['+919804310469'])

    @patch('cabot_alert_xoxzo.models.XoxzoAlert._send_xoxzo_alert')
    def test_failure_alert(self, fake_xoxzo_alert):
        self.service.overall_status = Service.CALCULATED_FAILING_STATUS
        self.service.old_overall_status = Service.PASSING_STATUS
        self.service.save()
        self.service.alert()
        fake_xoxzo_alert.assert_called_with(self.service,['+919804310469'])
