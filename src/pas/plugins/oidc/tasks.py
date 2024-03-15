
from collective.celery import task


@task(name='pas.plugins.oidc.create_or_update_user')
def create_or_update_user(context, userinfo):
    context._createOrUpdateUser(userinfo)


@task(name='pas.plugins.oidc.create_groups')
def create_groups(context, userinfo):
    context._createGroups(userinfo)
