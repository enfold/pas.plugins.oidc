"""Module where all interfaces, events and exceptions live."""
from pas.plugins.oidc import _
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IPasPluginsOidcLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IKeycloakSettings(Interface):
    """Keycloak group plugin settings"""

    enabled = schema.Bool(
        title=_("Use Groups from Keycloak"),
        required=False,
        default=False,
    )

    server_url = schema.TextLine(
        title=_("Keycloak base url"),
        description=_(
            "help_server_url",
            default="Base url for the Keycloak instance to be used",
        ),
        required=False,
        default="",
    )
    realm_name = schema.TextLine(
        title=_("Realm name"),
        description=_(
            "help_realm_name",
            default="Realm to be used for Groups.",
        ),
        required=False,
        default="",
    )

    username = schema.TextLine(
        title=_("Keycloak username"),
        description=_(
            "help_username",
            default="Username for the user with admin privileges on Keycloak",
        ),
        required=False,
        default="",
    )

    password = schema.TextLine(
        title=_("Keycloak password"),
        description=_(
            "help_password",
            default="Password for the user with admin privileges on Keycloak",
        ),
        required=False,
        default="",
    )

    client_id = schema.TextLine(
        title=_("Keycloak client_id"),
        description=_(
            "help_client_id",
            default="Client ID for Keycloak REST API.",
        ),
        required=False,
        default="",
    )

    client_secret = schema.TextLine(
        title=_("Keycloak client_secret"),
        description=_(
            "help_client_secret",
            default="Client Secret for Keycloak REST API.",
        ),
        required=False,
        default="",
    )

    verify = schema.Bool(
        title=_("Verify Keycloak server certificate"),
        required=False,
        default=True,
    )
