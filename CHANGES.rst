Changelog
=========


1.0.1+enfold10 (2024-12-18)
---------------------------

- Add some debugging code.
  [enfold]


1.0.1+enfold9 (2024-06-07)
--------------------------

- Use email for login.
  [enfold]


1.0.1+enfold8 (2024-05-22)
--------------------------

- Add missing return statement in login view __call__ method.
  [enfold]


1.0.1+enfold7 (2024-05-20)
--------------------------

- If came_from is the callback URL change it to the portal URL.
  [enfold]


1.0.1+enfold6 (2024-05-10)
--------------------------

- Enable retries.
  [enfold]

- Pass in request to plone.api.portal.show_message.
  [enfold]


1.0.1+enfold5 (2024-05-07)
--------------------------

- Don't expect HTTP_REFERER to be there when logging info from RequestError on callback view.
  [enfold]


1.0.1+enfold4 (2024-04-26)
--------------------------

- Change permission for login, require_login, and callback views to zope.Public.
  [enfold]


1.0.1+enfold3 (2024-04-11)
--------------------------

- Create or update user synchronously if site is not in readonly.
  [enfold]

- Add logging to debug missing response error.
  [enfold]


1.0.1+enfold2 (2024-03-18)
--------------------------

- Split async task into a task to create/update the user and a task to create
  groups.
  [enfold]


1.0.1+enfold1 (2024-03-12)
--------------------------

- Add first_name and last_name user attributes.
  [enfold]

- Add async task to add/update user.
  [enfold]


1.0.0 (2023-11-11)
------------------

- Allow dict instances to hold userinfo
  [erral]

1.0a6 (2023-07-20)
------------------

- Added Spanish translation
  [macagua]

- Added improvements about i18n support
  [macagua]

- Drop python 2.7 and Plone 4 support
  [erral]

- Add support for the post_logout parameter for logout api.
  [ramiroluz]


1.0a5 (2023-04-05)
------------------

- Catch exceptions during the OAuth process
  [erral]
- Update the plugin to make challenges.
  An anonymous user who visits a page for which you have to be authenticated,
  is redirected to the new require_login view on the plugin.
  This works the same way as the standard require_login page of Plone.
  [maurits]
- Add a property for the default userinfo instead of using only sub.
  [eikichi18]


1.0a4 (2023-01-16)
------------------

- Call getProperty only once when getting redirect_uris or scope.
  [maurits]

- use getProperty accessor
  [mamico]


1.0a3 (2022-10-30)
------------------

- Removed the hardcoded auth cookie name
  [alecghica]
- Fixed Python compatibility with version >= 3.6
  [alecghica]
- check if url is in portal before redirect #2
  [erral]
- manage came_from
  [mamico]

1.0a2 (unreleased)
------------------

- do userinforequest if there is a client.userinfo_endpoint
  [mamico]

1.0a1 (unreleased)
------------------

- Initial release.
  [mamico]
