import json
import os
import time

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from dashboard.models import PipeLine, PipeLineResult


class TestViews(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        get_user_model().objects.all().delete()
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

    def test_livelog_return_correct_file_content(self):
        user = get_user_model().objects.all().first()
        pipeline = PipeLine.objects.create(user=user, name="TEST", description="DESC", repo_url="http://google.com",
                                           script="test")
        pipeline.save()
        pipeline_result = PipeLineResult.objects.create(pipeline=pipeline, language='a', revision='', branch='',
                                                        installation_id=1,
                                                        log_file_name='test')
        pipeline_result.save()
        os.makedirs('logs', exist_ok=True)
        with open('logs/test.log', 'w+') as f:
            f.write("test message")
        response = self.client.get(reverse('dashboard:pipeline_build_livelog',
                                           kwargs={'pk': pipeline_result.pipeline.pk, 'id': pipeline_result.pk,
                                                   'current_size': 0}))
        self.assertContains(response, 'test message')
        pipeline_result.log_file_name = "doesnt exists"
        pipeline_result.save()

        response = self.client.get(reverse('dashboard:pipeline_build_livelog',
                                           kwargs={'pk': pipeline_result.pipeline.pk, 'id': pipeline_result.pk,
                                                   'current_size': 0}))
        self.assertEquals('', json.loads(response.content.decode())['text'])

    def test_livelog_ids_mismatch(self):
        user = get_user_model().objects.all().first()
        PipeLine.objects.create(user=user, name="TEST", description="DESC", repo_url="http://google.com",
                                script="test").save()
        pipeline = PipeLine.objects.create(user=user, name="TEST", description="DESC", repo_url="http://google.com",
                                           script="test")
        pipeline.save()

        pipeline_result = PipeLineResult.objects.create(pipeline=pipeline, language='a', revision='', branch='',
                                                        installation_id=1,
                                                        log_file_name='test')
        pipeline_result.save()
        response = self.client.get(reverse('dashboard:pipeline_build_livelog',
                                           kwargs={'pk': 1, 'id': pipeline_result.pk,
                                                   'current_size': 0}))
        self.assertEquals(404, response.status_code)


class TestViewsGeck(StaticLiveServerTestCase):
    def setUp(self):
        get_user_model().objects.create_user(username='test', password='test')
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_build_details_displays_correct_data(self):
        user = get_user_model().objects.all().first()
        pipeline = PipeLine.objects.create(user=user, name="TEST", description="DESC", repo_url="http://google.com",
                                           script="test")
        pipeline.save()
        pipeline_result = PipeLineResult.objects.create(pipeline=pipeline, language='a', revision='', branch='',
                                                        installation_id=1,
                                                        log_file_name='test')
        pipeline_result.save()
        os.makedirs('logs', exist_ok=True)
        with open('logs/test.log', 'w+') as f:
            f.write("test message")

        self.browser.get(self.live_server_url + reverse('dashboard:pipeline_build_details', kwargs={'pk': pipeline.pk,
                                                                                                    'id': pipeline_result.pk}))
        time.sleep(1)
        self.assertIn('test&nbsp;message', self.browser.page_source)


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
        self.assertIn('This password is too short. It must contain at least 9 characters.', self.browser.page_source)

    def test_registration_empty_fields_error_displayed(self):
        username = ''
        password = ''

        self.register_user(username, password)
        self.browser.find_element_by_class_name('invalid-feedback')
        self.assertIn('This field is required.', self.browser.page_source)
        self.assertEquals(self.browser.page_source.count('This field is required.'), 3)

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


class TestProfileView(TestCase):
    def setUp(self):
        self.client = Client()
        get_user_model().objects.all().delete()
        get_user_model().objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')

    def test_view_has_both_forms(self):
        response = self.client.get(reverse('dashboard:profile'))
        self.assertContains(response, 'profile_form')
        self.assertContains(response, 'password_form')

    def test_details_change_successful(self):
        self.client.post(reverse('dashboard:profile'),
                                 {'last_name': 'lastname', 'first_name': 'firstname', 'email': 'email@mail.com'})
        user = get_user_model().objects.all().first()
        self.assertEquals(user.first_name, 'firstname')
        self.assertEquals(user.last_name, 'lastname')
        self.assertEquals(user.email, 'email@mail.com')
