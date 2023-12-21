"""Init and utils."""
from AccessControl.Permissions import manage_users as ManageUsers
from Products.PluggableAuthService import PluggableAuthService as PAS
from Products.PluggableAuthService.permissions import ManageGroups
from zope.i18nmessageid import MessageFactory

import logging


PACKAGE_NAME = "pas.plugins.oidc"
PLUGIN_ID = "oidc"
KEYCLOAK_GROUPS_PLUGIN_ID = "groups_keycloak"


_ = MessageFactory(PACKAGE_NAME)

logger = logging.getLogger(PACKAGE_NAME)


def initialize(context):  # pragma: no cover
    """Initializer called when used as a Zope 2 product."""
    from pas.plugins.oidc.plugins import challenge
    from pas.plugins.oidc.plugins import group

    PAS.registerMultiPlugin(challenge.OIDCPlugin.meta_type)

    context.registerClass(
        challenge.OIDCPlugin,
        permission=ManageUsers,
        constructors=(challenge.add_oidc_plugin,),
    )

    PAS.registerMultiPlugin(group.KeycloakGroupsPlugin.meta_type)
    context.registerClass(
        group.KeycloakGroupsPlugin,
        permission=ManageGroups,
        constructors=(challenge.add_oidc_plugin,),
    )
