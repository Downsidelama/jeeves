def get_social_uid(backend, user, response, *args, **kwargs):
    """Saves the GitHub ID of the user."""
    user.social_uid = kwargs['uid']
    user.save()
