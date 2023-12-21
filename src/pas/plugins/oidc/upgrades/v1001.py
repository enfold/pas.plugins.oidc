from pas.plugins.oidc import PLUGIN_ID
from pas.plugins.oidc.utils import setup
from plone import api
from Products.GenericSetup.tool import SetupTool


def activate_challenge_plugin(setup_tool: SetupTool):
    pas = api.portal.get_tool("acl_users")
    setup.activate_plugin(pas, PLUGIN_ID, "IChallengePlugin", move_to_top=True)
