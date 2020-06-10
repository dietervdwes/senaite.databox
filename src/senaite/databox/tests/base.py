# -*- coding: utf-8 -*-

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.app.testing.bbb_at import PloneTestCase
from plone.protect.authenticator import createToken
from plone.testing.zope import Browser
from senaite.health.tests.layers import BASE_TESTING


class BaseTestCase(PloneTestCase):
    """Use for test cases which do not rely on the demo data
    """
    layer = BASE_TESTING

    def setUp(self):
        super(BaseTestCase, self).setUp()
        # Fixing CSRF protection
        # https://github.com/plone/plone.protect/#fixing-csrf-protection-failures-in-tests
        self.request = self.layer["request"]
        # Disable plone.protect for these tests
        self.request.form["_authenticator"] = createToken()
        # Eventuelly you find this also useful
        self.request.environ["REQUEST_METHOD"] = "POST"

        setRoles(self.portal, TEST_USER_ID, ["LabManager", "Manager"])

        # Default skin is set to "Sunburst Theme"!
        # => This causes an `AttributeError` when we want to access
        #    e.g. 'guard_handler' FSPythonScript
        self.portal.changeSkin("Plone Default")

    def getBrowser(self,
                   username=TEST_USER_NAME,
                   password=TEST_USER_PASSWORD,
                   loggedIn=True):

        # Instantiate and return a testbrowser for convenience
        browser = Browser(self.portal)
        browser.addHeader("Accept-Language", "en-US")
        browser.handleErrors = False
        if loggedIn:
            browser.open(self.portal.absolute_url())
            browser.getControl("Login Name").value = username
            browser.getControl("Password").value = password
            browser.getControl("Log in").click()
            self.assertTrue("You are now logged in" in browser.contents)
        return browser
