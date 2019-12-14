def get_social_uid(backend, user, response, *args, **kwargs):
    """Saves the GitHub ID of the user."""
    user.social_uid = kwargs['uid']
    user.save()


def get_email(backend, user, response, *args, **kwargs):
    """Saves the GitHub email of the user."""
    try:
        email = kwargs['email']
        if email is not None:
            user.email = email
        user.save()
    except:
        pass
