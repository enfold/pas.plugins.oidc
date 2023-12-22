from plone import api
from zope.component.hooks import setSite

import pytest


@pytest.fixture()
def portal(integration, keycloak, keycloak_api):
    portal = integration["portal"]
    setSite(portal)
    plugin = portal.acl_users.oidc
    with api.env.adopt_roles(["Manager", "Member"]):
        for key, value in keycloak.items():
            setattr(plugin, key, value)
        for key, value in keycloak_api.items():
            name = f"keycloak_groups.{key}"
            api.portal.set_registry_record(name, value)
    return portal
