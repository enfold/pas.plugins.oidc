from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection
from keycloak.exceptions import KeycloakGetError
from pas.plugins.oidc import logger
from plone import api
from plone.memoize import ram
from Products.PlonePAS.interfaces.group import IGroupIntrospection
from Products.PlonePAS.plugins.group import PloneGroup
from Products.PluggableAuthService.interfaces.plugins import IGroupEnumerationPlugin
from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin
from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
from Products.PluggableAuthService.permissions import ManageGroups
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from time import time
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple
from zope.interface import implementer
from zope.interface import Interface


def config(key: str) -> Any:
    """Get registry configuration for a given key."""
    name = f"keycloak_groups.{key}"
    return api.portal.get_registry_record(name=name)


_ATTRS_NOT_WRAPPED = [
    "id",
    "_members",
    "_roles",
]


class OIDCGroup(PloneGroup):
    security = ClassSecurityInfo()

    @security.public
    def addMember(self, id) -> None:
        logger.info(f"{self._id} does not support user assignment")

    @security.public
    def removeMember(self, id) -> None:
        logger.info(f"{self._id} does not support user removal")


class IKeycloakGroupsPlugin(Interface):
    """Interface for PAS plugin for using groups in Keycloak"""


@implementer(IKeycloakGroupsPlugin)
class KeycloakGroupsPlugin(BasePlugin):
    """PAS Plugin Providing Group information from Keycloak."""

    meta_type = "Keycloak Group Plugin"
    security = ClassSecurityInfo()

    @property
    @ram.cache(lambda *args: time() // (60 * 2))
    def _available_roles(self) -> List[str]:
        """Return available roles in Portal."""
        member_tool = api.portal.get_tool("portal_membership")
        return [r for r in member_tool.getPortalRoles() if r != "Owner"]

    def _wrap_group(self, group_info: dict) -> Optional[OIDCGroup]:
        """Given a dictionary with group information, return a OIDCGroup."""
        group = OIDCGroup(group_info["id"], group_info["title"])
        # Add title, description properties to the group object
        data = {k: v for k, v in group_info.items() if k not in _ATTRS_NOT_WRAPPED}
        group.addPropertysheet("temp", data)
        return group

    @property
    def _connection_settings(self) -> dict:
        """Keycloak REST API connection settings."""
        enabled = config("enabled")
        if enabled:
            return {
                "server_url": config("server_url"),
                "username": config("username"),
                "password": config("password"),
                "realm_name": config("realm_name"),
                "client_id": config("client_id"),
                "client_secret_key": config("client_secret"),
                "verify": config("verify"),
            }
        else:
            return {}

    @security.private
    def is_plugin_active(self, iface) -> bool:
        """Check if Plugin is active for given interface."""
        enabled = config("enabled")
        if not enabled:
            return False
        pas = self._getPAS()
        ids = pas.plugins.listPluginIds(iface)
        return self.getId() in ids

    def get_rest_api_client(self) -> KeycloakAdmin:
        settings = self._connection_settings
        keycloak_connection = KeycloakOpenIDConnection(**settings)
        keycloak_admin = KeycloakAdmin(connection=keycloak_connection)
        return keycloak_admin

    @property
    @ram.cache(lambda *args: time() // (60 * 2))
    def _groups(self) -> dict:
        """Query keycloak and return group information."""
        groups = {}
        plugin_id = self.getId()
        client = self.get_rest_api_client()
        groups_info = client.get_groups({"briefRepresentation": False})
        available_roles = self._available_roles
        for item in groups_info:
            roles = [r for r in item.get("realmRoles", []) if r in available_roles]
            groups[item["id"]] = {
                "id": item["id"],
                "title": item["name"],
                "description": item["path"],
                "pluginid": plugin_id,
                "groupid": item["id"],
                "principal_type": "group",
                "_roles": roles,
            }
        return groups

    def enumerateGroups(
        self,
        id=None,
        title=None,
        exact_match=False,
        sort_by=None,
        max_results=None,
        **kw,
    ):
        """Enumerate Groups.
        -> ( group_info_1, ... group_info_N )

        o Return mappings for groups matching the given criteria.

        o 'id' in combination with 'exact_match' true, will
          return at most one mapping per supplied ID ('id' and 'login'
          may be sequences).

        o If 'exact_match' is False, then 'id' may be treated by
          the plugin as "contains" searches (more complicated searches
          may be supported by some plugins using other keyword arguments).

        o If 'sort_by' is passed, the results will be sorted accordingly.
          known valid values are 'id' (some plugins may support others).

        o If 'max_results' is specified, it must be a positive integer,
          limiting the number of returned mappings.  If unspecified, the
          plugin should return mappings for all groups satisfying the
          criteria.

        o Minimal keys in the returned mappings:

          'id' -- (required) the group ID

          'pluginid' -- (required) the plugin ID (as returned by getId())

          'properties_url' -- (optional) the URL to a page for updating the
                              group's properties.

          'members_url' -- (optional) the URL to a page for updating the
                           principals who belong to the group.

        o Plugin *must* ignore unknown criteria.

        o Plugin may raise ValueError for invalid criteria.

        o Insufficiently-specified criteria may have catastrophic
          scaling issues for some implementations.
        """
        default = ()
        if not self.is_plugin_active(IGroupEnumerationPlugin):
            return default
        groups = self._groups
        if not groups:
            return default
        matches = []
        key = None
        if id or title:
            key = "id" if id else "title"
            value = id if id else title
        if key:
            matches = (
                [g for g in groups.values() if g[key] == value]
                if exact_match
                else [g for g in groups.values() if value in g[key]]
            )
        else:  # show all
            matches = list(groups.values())
        if sort_by == "id":
            matches = sorted(matches)
        ret = []
        for item in matches:
            ret.append(item)
        if max_results and len(ret) > max_results:
            ret = ret[:max_results]
        return tuple(ret)

    #
    #   IGroupsPlugin implementation
    #
    @security.private
    def getGroupsForPrincipal(self, principal, request=None) -> Tuple[str]:
        """See IGroupsPlugin."""
        if not self.is_plugin_active(IGroupsPlugin):
            return tuple()
        client = self.get_rest_api_client()
        try:
            groups = client.get_user_groups(user_id=principal.getId())
        except KeycloakGetError as exc:
            if exc.response_code == 404:
                logger.debug(f"{principal.getId()} not found in OIDC provider")
            else:
                logger.debug(
                    f"Error {exc.response_code} looking groups for {principal.getId()}"
                )
            return []
        return tuple([x.get("id") for x in groups])

    #
    #   (notional)IZODBGroupManager interface
    #
    @security.protected(ManageGroups)
    def listGroupIds(self) -> Tuple[str]:
        """-> (group_id_1, ... group_id_n)"""
        if not self.is_plugin_active(IGroupsPlugin):
            return tuple()
        return tuple(group_id for group_id in self._groups.keys())

    @security.protected(ManageGroups)
    def listGroupInfo(self) -> Tuple[dict]:
        """-> (dict, ...dict)

        o Return one mapping per group, with the following keys:

          - 'id'
        """
        if not self.is_plugin_active(IGroupsPlugin):
            return tuple()
        return tuple(group_info for group_info in self._groups.values())

    def _get_group_info(self, group_id: str) -> dict:
        default = None
        group_info = self._groups.get(group_id, default)
        if not group_info:
            return group_info
        # Get Members
        client = self.get_rest_api_client()
        try:
            members = client.get_group_members(group_id=group_id)
        except KeycloakGetError as exc:
            logger.debug(f"Error {exc.response_code} looking up members for {group_id}")
            members = []
        group_info["_members"] = [member["id"] for member in members]
        return group_info

    @security.protected(ManageGroups)
    def getGroupInfo(self, group_id: str) -> Optional[dict]:
        """group_id -> dict"""
        if not self.is_plugin_active(IGroupsPlugin):
            return None
        group_info = self._get_group_info(group_id)
        return group_info

    def getGroupById(self, group_id: str) -> Optional[OIDCGroup]:
        """Return the portal_groupdata object for a group corresponding to this id."""
        if not self.is_plugin_active(IGroupsPlugin):
            return None
        group_info = self.getGroupInfo(group_id)
        return self._wrap_group(group_info) if group_info else None

    def getGroups(self) -> List[OIDCGroup]:
        """Return an iterator of the available groups."""
        if not self.is_plugin_active(IGroupsPlugin):
            return []
        return [self.getGroupById(group_id) for group_id in self.getGroupIds()]

    def getGroupIds(self) -> List[str]:
        """Return a list of the available groups."""
        if not self.is_plugin_active(IGroupsPlugin):
            return []
        return [group_id for group_id in self._groups.keys()]

    def getGroupMembers(self, group_id: str) -> Tuple[str]:
        """Return the members of a group with the given group_id."""
        default = tuple()
        if self.is_plugin_active(IGroupsPlugin) and group_id in self._groups:
            client = self.get_rest_api_client()
            try:
                members = client.get_group_members(group_id=group_id)
            except KeycloakGetError as exc:
                logger.debug(
                    f"Error {exc.response_code} looking up members for {group_id}"
                )
                members = default
            return tuple(member["id"] for member in members)
        return default

    #
    #   IRolesPlugin implementation
    #
    @security.private
    def getRolesForPrincipal(self, principal, request=None) -> Tuple[str]:
        """Return roles for a given principal (See IRolesPlugin).

        We only care about principals(groups) defined in this plugin.
        """
        principal_id = principal.getId()
        default = tuple()
        if self.is_plugin_active(IGroupsPlugin) and principal_id in self._groups:
            group_info = self._get_group_info(principal_id)
            if group_info:
                return tuple(group_info.get("_roles", default))
        return default


InitializeClass(KeycloakGroupsPlugin)


classImplements(
    KeycloakGroupsPlugin,
    IKeycloakGroupsPlugin,
    IGroupsPlugin,
    IGroupIntrospection,
    IGroupEnumerationPlugin,
    IRolesPlugin,
)
