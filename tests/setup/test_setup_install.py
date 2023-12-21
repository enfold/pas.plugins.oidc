from pas.plugins.oidc import plugins
from pas.plugins.oidc import PACKAGE_NAME
from pas.plugins.oidc import PLUGIN_ID
from pas.plugins.oidc import KEYCLOAK_GROUPS_PLUGIN_ID
from plone import api

import pytest


class TestSetupInstall:
    @pytest.fixture(autouse=True)
    def _initialize(self, portal):
        self.portal = portal

    def test_addon_installed(self, installer):
        assert installer.is_product_installed(PACKAGE_NAME) is True

    def test_latest_version(self, profile_last_version):
        """Test latest version of default profile."""
        assert profile_last_version(f"{PACKAGE_NAME}:default") == "1010"

    def test_browserlayer(self, browser_layers):
        """Test that IPasPluginsOidcLayer is registered."""
        from pas.plugins.oidc.interfaces import IPasPluginsOidcLayer

        assert IPasPluginsOidcLayer in browser_layers

    @pytest.mark.parametrize(
        "plugin_id",
        [
            KEYCLOAK_GROUPS_PLUGIN_ID,
            PLUGIN_ID,
        ]
    )
    def test_plugin_added(self, plugin_id):
        """Test if plugin is added to acl_users."""
        pas = api.portal.get_tool("acl_users")
        assert plugin_id in pas.objectIds()

    @pytest.mark.parametrize(
        "plugin_id,klass",
        [
            (KEYCLOAK_GROUPS_PLUGIN_ID, plugins.KeycloakGroupsPlugin),
            (PLUGIN_ID, plugins.OIDCPlugin),
        ]
    )
    def test_plugin_is_oidc(self, plugin_id, klass):
        """Test if we have the correct plugin."""
        pas = api.portal.get_tool("acl_users")
        plugin = getattr(pas, plugin_id)
        assert isinstance(plugin, klass)
