from pas.plugins.oidc.utils import setup
from Products.CMFPlone.interfaces import INonInstallable
from Products.GenericSetup.tool import SetupTool
from typing import List
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self) -> List[str]:
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "pas.plugins.oidc:uninstall",
        ]


def post_install(setup_tool: SetupTool):
    """Post install script"""
    for klass, plugin_id, title, should_activate, move_to_top in setup.PLUGINS:
        setup.add_pas_plugin(klass, plugin_id, title, should_activate, move_to_top)


def uninstall(setup_tool: SetupTool):
    """Uninstall script"""
    for klass, plugin_id, *_ in setup.PLUGINS:
        setup.remove_pas_plugin(klass, plugin_id)
