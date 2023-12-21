from pas.plugins.oidc import logger
from pas.plugins.oidc.utils import setup
from Products.GenericSetup.tool import SetupTool


def add_keycloak_plugin(setup_tool: SetupTool):
    plugins = [
        setup.PLUGIN_GROUP,
    ]
    for klass, plugin_id, title, should_activate, move_to_top in plugins:
        setup.add_pas_plugin(klass, plugin_id, title, should_activate, move_to_top)
        logger.info(f"Added {plugin_id} to acl_users.")
