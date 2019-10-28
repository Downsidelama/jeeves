import time

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from dashboard.models import PipeLine


class TestViews(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        get_user_model().objects.create_user(username='test', password='test')

    def login(self):
        self.client.login(username='test', password='test')

    def test_not_logged_in_cant_view_protected_pages(self):
        page = self.client.get('/', follow=True)
        self.assertTrue(len(page.redirect_chain) > 0)

    def test_logged_in_no_redirect(self):
        self.login()
        page = self.client.get('/')
        self.assertEquals(page.status_code, 200)

    def test_no_pipelines_added_nothing_displayed(self):
        self.login()
        page = self.client.get('/')
        self.assertContains(page, 'Add a pipeline!')

    def test_add_pipeline_shows_up_on_home_page(self):
        self.login()
        user = get_user_model().objects.all().first()
        PipeLine.objects.create(user=user, name="TEST", description="DESC", repo_url="https://google.com/",
                                script="test")
        response = self.client.get('/')
        self.assertContains(response, "DESC")

    def test_add_pipeline_has_details_view(self):
        self.login()
        user = get_user_model().objects.all().first()
        pipeline = PipeLine.objects.create(user=user, name="TEST", description="DESC", repo_url="https://google.com/",
                                           script="test")
        response = self.client.get(pipeline.get_absolute_url())
        self.assertContains(response, 'DESC')


class TestRegistration(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_register_with_correct_details(self):
        username = 'test_account'
        password = 'R&6w8KR$eEhm'

        self.register_user(password, username)
        self.browser.find_element_by_id('password')
        self.assertEquals(self.live_server_url + "{}?successful_registration".format(reverse('login')),
                          self.browser.current_url)
        self.assertEquals(get_user_model().objects.get(username=username).username, username)

    def test_registration_weak_password_error_displayed(self):
        username = 'test_account'
        password = 'a'

        self.register_user(password, username)
        self.browser.find_element_by_class_name('invalid-feedback')
        self.assertIn('This password is too short. It must contain at least 8 characters.', self.browser.page_source)

    def register_user(self, password, username):
        self.browser.get(self.live_server_url + reverse('dashboard:registration'))
        self.assertIn('Jeeves - Registration', self.browser.title)
        username1 = self.browser.find_element_by_id('username')
        password1 = self.browser.find_element_by_id('password1')
        password2 = self.browser.find_element_by_id('password2')
        username1.send_keys(username)
        password1.send_keys(password)
        password2.send_keys(password)
        self.browser.find_element_by_name('reg_form').submit()
