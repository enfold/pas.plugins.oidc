from pas.plugins.oidc.interfaces import IKeycloakSettings
from pas.plugins.oidc.utils import setup
from plone import api
from plone.registry.events import RecordModifiedEvent


def keycloak_settings_modified(_: IKeycloakSettings, event: RecordModifiedEvent):
    """A setting in the keycloak group was modified."""
    field_name = event.record.fieldName
    if field_name == "enabled":
        pas = api.portal.get_tool("acl_users")
        plugin_id = setup.PLUGIN_GROUP[1]
        plugin = getattr(pas, plugin_id, None)
        value = event.record.value
        if plugin:
            interfaces = setup.interfaces_for_plugin(pas, plugin_id)
            if value:
                # Activate the plugin
                move_to_top = setup.PLUGIN_GROUP[-1]
                for interface_name in interfaces:
                    _move_to_top = interface_name in move_to_top
                    setup.activate_plugin(pas, plugin_id, interface_name, _move_to_top)
            else:
                for interface_name in interfaces:
                    setup.deactivate_plugin(pas, plugin_id, interface_name)
