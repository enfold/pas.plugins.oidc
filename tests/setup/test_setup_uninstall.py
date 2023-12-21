from pas.plugins.oidc import PACKAGE_NAME
from pas.plugins.oidc import PLUGIN_ID
from pas.plugins.oidc import KEYCLOAK_GROUPS_PLUGIN_ID
from plone import api

import pytest


class TestSetupUninstall:
    @pytest.fixture(autouse=True)
    def uninstalled(self, installer):
        installer.uninstall_product(PACKAGE_NAME)

    def test_product_uninstalled(self, installer):
        """Test if pas.plugins.oidc is cleanly uninstalled."""
        assert installer.is_product_installed(PACKAGE_NAME) is False

    def test_browserlayer(self, browser_layers):
        """Test that IPasPluginsOidcLayer is removed."""
        from pas.plugins.oidc.interfaces import IPasPluginsOidcLayer

        assert IPasPluginsOidcLayer not in browser_layers

    @pytest.mark.parametrize(
        "plugin_id",
        [
            KEYCLOAK_GROUPS_PLUGIN_ID,
            PLUGIN_ID
        ]
    )
    def test_plugin_removed(self, portal, plugin_id):
        """Test if plugin is removed to acl_users."""
        pas = api.portal.get_tool("acl_users")
        assert plugin_id not in pas.objectIds()
