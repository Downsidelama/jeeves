import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest


class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_login_arrive_at_home_page(self):
        self.browser.get('http://localhost:8000')

        self.assertIn('Jeeves', self.browser.title)
        username_input = self.browser.find_element_by_id('username')
        username_input.send_keys('root')
        password_input = self.browser.find_element_by_id('password')
        password_input.send_keys('a')
        password_input.send_keys(Keys.ENTER)

        spans = self.browser.find_elements_by_class_name('text-default')
        self.assertIn('root', [span.text for span in spans])

        self.fail('Finish the test')

