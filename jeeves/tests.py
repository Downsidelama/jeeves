import time

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from jeeves import settings

User = get_user_model()
TEST_USERNAME = 'root'
TEST_PASSWORD = 'a'


class NewVisitorTest(StaticLiveServerTestCase):
    def setUp(self):
        User.objects.create_user(username=TEST_USERNAME, password=TEST_PASSWORD)
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_login_add_and_run_pipeline(self):
        self.browser.get(self.live_server_url)

        self.assertIn('Jeeves', self.browser.title)

        # Log in
        username_input = self.browser.find_element_by_id('username')
        username_input.send_keys(TEST_USERNAME)
        password_input = self.browser.find_element_by_id('password')
        password_input.send_keys(TEST_PASSWORD)
        password_input.send_keys(Keys.ENTER)

        # I should be logged in
        spans = self.browser.find_elements_by_class_name('text-default')
        self.assertIn('root', [span.text for span in spans])

        # I want to add a new pipeline
        new_pipeline_button = self.browser.find_element_by_link_text("Add new pipeline")
        new_pipeline_button.click()

        add_pipeline_url = self.browser.current_url

        # Incorrect form
        name = self.browser.find_element_by_id('id_name')
        name.send_keys('Jeeves test CI')

        description = self.browser.find_element_by_id('id_description')
        description.send_keys('This is a description')

        repo_url = self.browser.find_element_by_id('id_repo_url')
        repo_url.send_keys('a')

        send_button = self.browser.find_element_by_tag_name('button')
        send_button.click()

        self.assertTrue('Enter a valid URL.' in self.browser.page_source)

        self.browser.get(add_pipeline_url)

        # Fill in the fields
        name = self.browser.find_element_by_id('id_name')
        name.send_keys('Jeeves test CI')

        description = self.browser.find_element_by_id('id_description')
        description.send_keys('This is a description')

        repo_url = self.browser.find_element_by_id('id_repo_url')
        repo_url.send_keys('https://github.com/Downsidelama/jeeves')

        script = self.browser.find_element_by_css_selector('.CodeMirror textarea')

        script.send_keys('''language: python
python:
- "3.7"
install:
- pip install -r requirements.txt
script:
- python manage.py tests''')

        send_button = self.browser.find_element_by_tag_name('button')
        send_button.click()

        self.assertTrue('Start pipeline' in self.browser.page_source)

        start_pipeline_button = self.browser.find_element_by_link_text('Start pipeline')
        start_pipeline_button.click()
