from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import Client

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
