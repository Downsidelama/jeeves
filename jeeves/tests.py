import time

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        name.send_keys('Test Java Pipeline')

        description = self.browser.find_element_by_id('id_description')
        description.send_keys('This is a description')

        repo_url = self.browser.find_element_by_id('id_repo_url')
        repo_url.send_keys('https://github.com/LableOrg/java-maven-junit-helloworld')

        script = self.browser.find_element_by_css_selector('.CodeMirror textarea')
        script.send_keys('language: java')

        send_button = self.browser.find_element_by_tag_name('button')
        send_button.click()

        self.assertTrue('language: java' in self.browser.page_source)

        # I forgot something to fill in

        edit_pipeline_button = self.browser.find_element_by_partial_link_text('Edit pipeline')
        edit_pipeline_button.click()
        script = self.browser.find_element_by_css_selector('.CodeMirror textarea')
        script.send_keys(Keys.CONTROL + 'a')
        script.send_keys(Keys.DELETE)

        script.send_keys(('language: java\n'
                          'java:\n'
                          '- "8"\n'
                          '\n'
                          'script:\n'
                          '- apk add --no-cache firefox-esr\n'
                          '- wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz\n'
                          '- mkdir geckodriver\n'
                          '- tar -xzf geckodriver-v0.24.0-linux64.tar.gz -C geckodriver\n'
                          '- export PATH=$PATH:$PWD/geckodriver\n'
                          '- export MOZ_HEADLESS=1\n'
                          '- apk add maven\n'
                          '- mvn test\n'))

        send_button = self.browser.find_element_by_tag_name('button')
        send_button.click()

        # Start pipeline
        start_pipeline_button = self.browser.find_element_by_link_text('Start pipeline')
        start_pipeline_button.click()

        # View my pipelines

        view_pipeline = self.browser.find_element_by_partial_link_text('View all build')
        view_pipeline.click()

        # View my first build
        build10 = self.browser.find_element_by_partial_link_text('1.0')
        build10.click()

        try:
            WebDriverWait(self.browser, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'error-card')))
        except TimeoutException:
            WebDriverWait(self.browser, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'success-card')))
