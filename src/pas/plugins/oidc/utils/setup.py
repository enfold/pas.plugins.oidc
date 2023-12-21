from pas.plugins.oidc import KEYCLOAK_GROUPS_PLUGIN_ID
from pas.plugins.oidc import logger
from pas.plugins.oidc import PLUGIN_ID
from pas.plugins.oidc.plugins import KeycloakGroupsPlugin
from pas.plugins.oidc.plugins import OIDCPlugin
from plone import api
from Products.PluggableAuthService.PluggableAuthService import PluggableAuthService
from typing import List
from typing import Type
from typing import Union


PLUGIN_CHALLENGE = (
    OIDCPlugin,
    PLUGIN_ID,
    "OpenID Connect",
    True,
    [
        "IChallengePlugin",
    ],
)

PLUGIN_GROUP = (
    KeycloakGroupsPlugin,
    KEYCLOAK_GROUPS_PLUGIN_ID,
    "Keycloak Groups",
    False,
    [
        "IGroupsPlugin",
        "IGroupIntrospection",
        "IGroupEnumerationPlugin",
    ],
)


PLUGINS = [PLUGIN_CHALLENGE, PLUGIN_GROUP]


def interfaces_for_plugin(pas: PluggableAuthService, plugin_id: str) -> List[str]:
    """Given a plugin, return a list of interface names."""
    plugin = getattr(pas, plugin_id, None)
    if not plugin:
        return []
    plugins = pas.plugins
    interfaces = []
    for info in plugins.listPluginTypeInfo():
        interface = info["interface"]
        interface_name = info["id"]
        if plugin.testImplements(interface):
            interfaces.append(interface_name)
    return interfaces


def activate_plugin(
    pas: PluggableAuthService,
    plugin_id: str,
    interface_name: str,
    move_to_top: bool = False,
):
    if plugin_id not in pas.objectIds():
        raise ValueError(f"acl_users has no plugin {plugin_id}.")

    # This would activate one interface and deactivate all others:
    # plugin.manage_activateInterfaces([interface_name])
    # So only take over the necessary code from manage_activateInterfaces.
    plugins = pas.plugins
    iface = plugins._getInterfaceFromName(interface_name)
    if plugin_id not in plugins.listPluginIds(iface):
        plugins.activatePlugin(iface, plugin_id)
        logger.info(f"Activated interface {interface_name} for plugin {plugin_id}")

    if move_to_top:
        # Order some plugins to make sure our plugin is at the top.
        # This is not needed for all plugin interfaces.
        plugins.movePluginsTop(iface, [plugin_id])
        logger.info(f"Moved {plugin_id} to top of {interface_name}.")


def deactivate_plugin(pas: PluggableAuthService, plugin_id: str, interface_name: str):
    if plugin_id not in pas.objectIds():
        raise ValueError(f"acl_users has no plugin {plugin_id}.")
    plugins = pas.plugins
    iface = plugins._getInterfaceFromName(interface_name)
    plugins.deactivatePlugin(iface, plugin_id)
    logger.info(f"Deactivated interface {interface_name} for plugin {plugin_id}")


def add_pas_plugin(
    klass: Type,
    plugin_id: str,
    title: str,
    should_activate: bool,
    move_to_top: List[str],
) -> Union[KeycloakGroupsPlugin, OIDCPlugin]:
    """Add a new plugin to acl_users."""
    pas = api.portal.get_tool("acl_users")
    # Create plugin if it does not exist.
    if plugin_id not in pas.objectIds():
        plugin = klass(title=title)
        plugin.id = plugin_id
        pas._setObject(plugin_id, plugin)
        logger.info(f"Added {plugin_id} to acl_users.")
    plugin = getattr(pas, plugin_id)
    if not isinstance(plugin, klass):
        raise ValueError(f"Existing PAS plugin {plugin_id} is not a {klass}.")

    if should_activate:
        activate = interfaces_for_plugin(pas, plugin_id)
        for interface_name in activate:
            _move_to_top = interface_name in move_to_top
            activate_plugin(pas, plugin_id, interface_name, _move_to_top)
    return plugin


def remove_pas_plugin(klass: Type, plugin_id: str) -> bool:
    """Remove pas plugin from acl_users."""
    pas = api.portal.get_tool("acl_users")
    # Remove plugin if it exists.
    if plugin_id not in pas.objectIds():
        return False

    plugin = getattr(pas, plugin_id)
    if not isinstance(plugin, klass):
        logger.warning(
            f"PAS plugin {plugin_id} not removed: it is not a {klass.__name__}."
        )
        return False
    pas._delObject(plugin_id)
    logger.info(f"Removed {klass.__name__} {plugin_id} from acl_users.")
    return True
