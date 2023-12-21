from pas.plugins.oidc import _
from pas.plugins.oidc.interfaces import IKeycloakSettings
from pas.plugins.oidc.interfaces import IPasPluginsOidcLayer
from plone.app.registry.browser import controlpanel
from plone.restapi.controlpanels import RegistryConfigletPanel
from zope.component import adapter
from zope.interface import Interface


class KeycloakGroupSettingsForm(controlpanel.RegistryEditForm):
    schema = IKeycloakSettings
    schema_prefix = "keycloak_groups"
    label = _("Keycloak Group Plugin Settings")
    description = ""


class KeycloakGroupSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = KeycloakGroupSettingsForm


@adapter(Interface, IPasPluginsOidcLayer)
class KeycloakGroupSettingsConfigletPanel(RegistryConfigletPanel):
    """Control Panel endpoint"""

    schema = IPasPluginsOidcLayer
    configlet_id = "keycloak_groups"
    configlet_category_id = "plone-users"
    title = _("Keycloak Group settings")
    group = ""
    schema_prefix = "keycloak_groups"
