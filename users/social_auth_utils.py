def get_social_uid(backend, user, response, *args, **kwargs):
    user.social_uid = kwargs['uid']
    user.save()
