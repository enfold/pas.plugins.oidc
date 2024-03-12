
from collective.celery import task


@task(name='pas.plugins.oidc.remember_user')
def remember_user(context, userinfo):
    context.rememberIdentity(userinfo)
