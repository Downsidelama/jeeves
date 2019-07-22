from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import github3
from github import Github
import time
import os
import jwt
from dotenv import load_dotenv


# @login_required
def index(request):
    context = {}
    return render(request, 'dashboard/index.html', context=context)


def get_github_client():
    load_dotenv()
    GITHUB_PRIVATE_KEY = os.getenv('GITHUB_PRIVATE_KEY')
    GITHUB_APP_IDENTIFIER = os.getenv('GITHUB_APP_IDENTIFIER')
    GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')

    message = {'iat': int(time.time()),
               'exp': int(time.time()) + (10 * 60),
               'iss': GITHUB_APP_IDENTIFIER}

    token = jwt.encode(message, GITHUB_PRIVATE_KEY.strip().encode(), 'RS256')
    print(token.decode())

    gh = Github(token.decode())
    # gh.login_as_app(GITHUB_PRIVATE_KEY.encode(), GITHUB_APP_IDENTIFIER, 600)
    return gh


@csrf_exempt
def event_handler(request):
    client = get_github_client()
    print(client.get_user())
    return HttpResponse("Hi!")


if __name__ == "__main__":
    client = get_github_client()
    for repo in client.get_user().get_repos():
        print(repo.name)
