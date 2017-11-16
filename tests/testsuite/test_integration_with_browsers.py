import os
import splinter
import pytest

DOMAIN = 'liquid.example.org'
URL = 'http://'+DOMAIN

ADMIN_USERNAME = 'testadmin'
ADMIN_PASSWORD = 'test-liquid.example.org'
HOTSPOT_SSID = 'testhotspotssid'
HOTSPOT_PASSWORD = 'testhotspotpassword'

APP_NAMES = [
    "Hoover",
    "Hypothesis",
    "DokuWiki",
    "Matrix",
    "Davros",
]

BROWSERS = [
    'firefox',
    'chrome',
]

BROWSER_OPTS = {
    'firefox': {
    },
    'chrome': {
        'service_args': ['--verbose', '--log-path=chromedriver.log'],
    },
}


WELCOME_FILE_PATH = '/var/lib/liquid/core/welcome_done'

def skip_if_welcome_not_set():
    if not os.path.isfile(WELCOME_FILE_PATH):
        pytest.skip('welcome not set')


@pytest.fixture(params=['firefox', 'chrome'])
def browser(request):
    browser_name = request.param
    with splinter.Browser(browser_name, headless=True, wait_time=10, **BROWSER_OPTS[browser_name]) as browser:
        browser.visit(URL)
        yield browser


@pytest.mark.parametrize('browser', ['firefox'], indirect=True)
def test_browser_welcome(browser):
    assert not os.path.isfile(WELCOME_FILE_PATH)

    assert browser.is_text_present("Liquid Investigations")
    assert browser.is_text_present("Congratulations")
    
    browser.fill('admin-username', ADMIN_USERNAME)
    browser.fill('admin-password', ADMIN_PASSWORD)
    browser.fill('hotspot-ssid', HOTSPOT_SSID)
    browser.fill('hotspot-password', HOTSPOT_PASSWORD)
    
    browser.find_by_text('Apply').click()

    assert browser.is_text_present("Liquid Investigations")
    assert browser.is_text_present("Your settings are being applied")
    assert browser.is_text_present("Wait a minute")

    assert os.path.isfile(WELCOME_FILE_PATH)


def test_view_home_page(browser):
    skip_if_welcome_not_set()
    assert browser.is_text_present("Liquid Investigations")

    for app_name in APP_NAMES:
        assert browser.is_text_present(app_name)


def test_login_into_home_page(browser):
    skip_if_welcome_not_set()
    assert browser.is_text_present("Liquid Investigations")

    # login
    browser.find_by_text('[login]').click()
    browser.fill('username', ADMIN_USERNAME)
    browser.fill('password', ADMIN_PASSWORD)
    browser.find_by_text('login').click()
    
    # check that we're logged in
    assert browser.is_text_present("Liquid Investigations")
    assert browser.is_text_present("[admin]")
    assert browser.is_text_present("[logout]")
    assert browser.is_text_present(ADMIN_USERNAME)

    # logout
    browser.find_by_text('[logout]').click()
    assert browser.is_text_present("[login]")
    assert not browser.is_text_present(ADMIN_USERNAME)


def test_login_into_dokuwiki(browser):
    skip_if_welcome_not_set()
    assert browser.is_text_present("Liquid Investigations")
    
    # navigate to dokuwiki and login
    browser.find_by_text('DokuWiki').click()
    assert browser.is_text_present("Permission Denied")
    browser.fill('u', ADMIN_USERNAME)
    browser.fill('p', ADMIN_PASSWORD)
    browser.find_by_css('#dw__login button[type=submit]').click()

    # we should be logged in now, let's check
    assert browser.is_text_present(ADMIN_USERNAME)
    assert browser.is_text_present("Admin")
    assert browser.is_text_present("Log Out")

    browser.find_by_text('Log Out').click()
    assert browser.is_text_present("Permission Denied")


def test_login_into_hypothesis(browser):
    skip_if_welcome_not_set()
    assert browser.is_text_present("Liquid Investigations")
    
    # navigate to hypothesis and login
    browser.find_by_text('Hypothesis').click()
    browser.find_by_text('Log in').click()
    browser.fill('username', ADMIN_USERNAME)
    browser.fill('password', ADMIN_PASSWORD)
    browser.find_by_css('#deformLog_in').click()

    # we should be logged in now, let's check
    assert browser.is_text_present(ADMIN_USERNAME)
    assert browser.is_text_present("How to get started")


def test_login_into_matrix(browser):
    skip_if_welcome_not_set()
    assert browser.is_text_present("Liquid Investigations")
    
    # navigate to matrix and login
    browser.find_by_text('Matrix').click()
    assert browser.is_text_present("Matrix ID (e.g. @bob:matrix.org or bob)")
    browser.find_by_css('#user_id').fill(ADMIN_USERNAME)
    browser.find_by_css('#password').fill(ADMIN_PASSWORD)
    browser.find_by_css('button#login').click()

    # we should be logged in now, let's check
    assert browser.is_text_present(ADMIN_USERNAME)
    assert browser.is_text_present("Welcome to homeserver")
    assert browser.is_text_present("Log out")

    browser.find_by_text('Log out').click()
    assert browser.is_text_present("Matrix ID (e.g. @bob:matrix.org or bob)")


def test_login_into_davros(browser):
    skip_if_welcome_not_set()
    assert browser.is_text_present("Liquid Investigations")
    
    # navigate to davros and login
    browser.find_by_text('Davros').click()
    browser.fill('username', ADMIN_USERNAME)
    browser.fill('password', ADMIN_PASSWORD)
    browser.find_by_text('login').click()

    assert browser.is_text_present(".gitkeep")
    assert browser.is_text_present("Updated")
    assert browser.is_text_present("Files in home")


def test_login_into_hoover(browser):
    skip_if_welcome_not_set()
    assert browser.is_text_present("Liquid Investigations")

    # login
    browser.find_by_text('[login]').click()
    browser.fill('username', ADMIN_USERNAME)
    browser.fill('password', ADMIN_PASSWORD)
    browser.find_by_text('login').click()
    
    # navigate to hoover
    browser.find_by_text('Hoover').click()

    # click on the menu and on "login"
    browser.find_by_id('loggedin-btngroup').click()
    assert browser.is_text_present("login")
    browser.find_by_text('login').click()

    # we should be logged in because oauth
    browser.find_by_id('loggedin-btngroup').click()
    assert browser.is_text_present("admin")
    assert browser.is_text_present("change password")
    assert browser.is_text_present("({}) logout".format(ADMIN_USERNAME))

    # let's wander around the hoover django admin
    browser.find_by_text('admin').click()
    assert browser.is_text_present("Site administration")
    assert browser.is_text_present("LOG OUT")

    # let's log out from the django admin
    browser.find_by_text('Log out').click()

    # and check that we're logged out
    browser.find_by_id('loggedin-btngroup').click()
    assert browser.is_text_present("login")

# no chrome on admin UI because clickin issues in menu
@pytest.mark.parametrize('browser', ['firefox'], indirect=True)
def test_navigation_through_admin(browser):
    skip_if_welcome_not_set()
    assert browser.is_text_present("Liquid Investigations")

    # login
    browser.find_by_text('[login]').click()
    browser.fill('username', ADMIN_USERNAME)
    browser.fill('password', ADMIN_PASSWORD)
    browser.find_by_text('login').click()

    browser.find_by_text('[admin]').click()

    # we're in the admin now
    assert browser.is_text_present("admin")
    assert browser.is_text_present("Logged in as: {}".format(ADMIN_USERNAME))

    # click on all the buttons
    browser.click_link_by_href('/admin-ui/status')
    assert browser.is_text_present("General Status")

    browser.click_link_by_href('/admin-ui/network')
    assert browser.is_text_present("Network Configuration")
    assert browser.is_text_present("Domain")
    assert browser.is_text_present(DOMAIN)
    assert browser.is_text_present("Lan configuration")
    assert browser.is_text_present(HOTSPOT_SSID)

    browser.click_link_by_href('/admin-ui/network/lan')
    # TODO test these; they don't show up as text because they're inside inputs
    #assert browser.is_text_present(HOTSPOT_SSID)
    #assert browser.is_text_present(HOTSPOT_PASSWORD)
    assert browser.is_text_present('Use Ethernet on LAN')

    browser.click_link_by_href('/admin-ui/network/wan')
    assert browser.is_text_present('DHCP')
    assert browser.is_text_present('Gateway')
    assert browser.is_text_present('DNS Server')

    browser.click_link_by_href('/admin-ui/network/ssh')
    assert browser.is_text_present('SSH')
    assert browser.is_text_present('Port')
    assert browser.is_text_present('Update')

    browser.click_link_by_href('/admin-ui/vpn')
    assert browser.is_text_present("VPN Configuration")
    assert browser.is_text_present("Server configuration")
    assert browser.is_text_present("Client configuration")
    assert browser.is_text_present("Connection count")

    browser.click_link_by_href('/admin-ui/vpn/server')
    assert browser.is_text_present("Enable VPN server")
    assert browser.is_text_present("Generate new key")
    assert browser.is_text_present("Active keys")

    browser.click_link_by_href('/admin-ui/vpn/client')
    assert browser.is_text_present("Enable VPN client")
    assert browser.is_text_present("Upload key")

    browser.click_link_by_href('/admin-ui/services')
    assert browser.is_text_present("Services")
    for app_name in APP_NAMES:
        assert browser.is_text_present(app_name.upper())
    for app_desc in ['Search Tool', 'Annotations', 'Chat', 'Wiki', 'File Sharing']:
        assert browser.is_text_present(app_name.upper())

    browser.click_link_by_href('/admin-ui/users')
    assert browser.is_text_present("Users")
    assert browser.is_text_present("Active users")
    assert browser.is_text_present("Inactive users")

    browser.click_link_by_href('/admin-ui/discovery')
    assert browser.is_text_present("Discovery")
    assert browser.is_text_present("Trusted nodes")
    assert browser.is_text_present("Untrusted nodes")

    browser.click_link_by_href('/admin-ui/about')
    assert browser.is_text_present("Lorem ipsum dolor sit amet")
