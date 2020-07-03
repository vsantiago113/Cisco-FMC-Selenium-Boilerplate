from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotVisibleException, \
    ElementNotInteractableException
import time
import os
import sys

'''
This code was made to work on FMC version 6.2.3.13 and 6.3.0 and it has not been tested on any other version.
This code might not work on older or newer versions.
'''

# Add to this list supported FMC versions that your code support or ones you tested.
supported_versions = ['6.2.3.13', '6.3.0']


def fmc_login(manager: str, username: str, password: str, version: str) -> webdriver:
    '''
    This function navigates to the login page, check if the page is asking to confirm the unsecure ssl and click on it
    if is there, then login, click on the button to login if there is a session already logged in an and make the
    browser full screen.

    :param manager: The Address of the Manager/FMC.
    :param username: The Manager/FMC login username.
    :param password: The Manager/FMC login password.
    :param version: The version of FMC you are using.
    :return: webdriver
    '''

    if version not in supported_versions:
        print('This version is not supported or this code have not been tested in this version.')
        sys.exit(1)

    # This capabilities are used to disabled all notifications and prompts when selenium starts.
    capabilities = {
        'browserName': 'chrome',
        'chromeOptions': {
            'useAutomationExtension': False,
            'forceDevToolsScreenshot': True,
            'args': ['--start-maximized', '--disable-infobars', '--disable-extensions']
        }
    }

    # Make sure you download the correct driver according to your web browser and browser version.
    driver = webdriver.Chrome('bins/chromedriver', desired_capabilities=capabilities)
    driver.implicitly_wait(1)  # This like waits one second before executing anything on the DOM.
    if manager.startswith('http'):
        driver.get('{}/login.cgi?'.format(manager))
    else:
        driver.get('https://{}/login.cgi?'.format(manager))
    time.sleep(3)

    # Used to acknowledge the unsecure ssl certificate if it prompts for it.
    try:
        advanced_button = driver.find_element(By.XPATH, '/html/body/div/div[2]/button[3]')
    except (NoSuchElementException, ElementNotVisibleException, ElementNotInteractableException):
        pass
    else:
        advanced_button.click()

        time.sleep(2)
        unsafe = driver.find_element(By.XPATH, '/html/body/div/div[3]/p[2]/a')
        unsafe.click()

    WebDriverWait(driver, 120).until(
        expected_conditions.presence_of_element_located(
            (By.ID,
             'username'))
    )  # Waits until it finds the username form field and timeout in 120 seconds.
    login_form_username = driver.find_element_by_id('username')
    login_form_username.send_keys(username)
    login_form_password = driver.find_element_by_id('password')
    login_form_password.send_keys(password)
    driver.maximize_window()
    login_form_password.submit()

    # Use to accept the notification indicating that there is already a session open for this account.
    time.sleep(3)
    try:
        proceed = driver.find_element(By.XPATH, '//*[@id="confirm_dialog"]/div[2]/input[1]')
    except (NoSuchElementException, ElementNotVisibleException, ElementNotInteractableException):
        pass
    else:
        proceed.click()

    # return the webdriver as driver
    return driver


def logout(driver: webdriver, manager: str) -> None:
    '''
    This function log you out and gracefully quits everything.

    :param driver: The web browser driver.
    :param manager: The Address of the Manager/FMC.
    :return: None
    '''
    time.sleep(5)
    if manager.startswith('http'):
        driver.get('{}/login.cgi?logout=1'.format(manager))
    else:
        driver.get('https://{}/login.cgi?logout=1'.format(manager))
    time.sleep(5)
    driver.quit()  # Gracefully quits everything.


def disabled_notifications(driver: webdriver, version) -> None:
    '''
    This function disables the notifications on the FMC to prevent the notification popups from crashing the selenium.

    :param driver: The web browser driver.
    :param version: The version of FMC you are using.
    :return: None
    '''

    if version == '6.2.3.13':
        tasks_icon = '/html/body/div[13]/div[1]/ul/li[12]/div/div[3]'
        gear_icon = '/html/body/div[13]/div[1]/ul/li[12]/div/div[4]/div[4]'
        notifications_icon = '/html/body/div[13]/div[1]/ul/li[12]/div/div[5]/ul/li/div/div/img'
        enabled_image = 'YgAAADuklEQVR42tWV7U9TZxiHnW7TLX'
        disabled_image = 'YgAAAC8UlEQVR42tWVXUuaYRjHKxmxsY'
    elif version == '6.3.0':
        tasks_icon = '/html/body/div[7]/div[2]/div/div[2]/div/ul/li[8]/div/div[3]'
        gear_icon = '/html/body/div[7]/div[2]/div/div[2]/div/ul/li[8]/div/div[4]/div[4]'
        notifications_icon = '/html/body/div[7]/div[2]/div/div[2]/div/ul/li[8]/div/div[5]/ul/li/div/div/img'
        enabled_image = 'YgAAADuklEQVR42tWV7U9TZxiHnW7TLX'
        disabled_image = 'YgAAAC8UlEQVR42tWVXUuaYRjHKxmxsY'
    else:
        tasks_icon = ''
        gear_icon = ''
        notifications_icon = ''
        enabled_image = ''
        disabled_image = ''

    time.sleep(2)
    WebDriverWait(driver, 120).until(
        expected_conditions.presence_of_element_located(
            (By.XPATH,
             tasks_icon))
    )  # Waits until it finds the tasks icon on the upper right corner and timeout in 120 seconds.
    tasks_element = driver.find_element(By.XPATH, tasks_icon)
    tasks_element.click()

    gear_element = driver.find_element(By.XPATH, gear_icon)
    gear_element.click()

    notifications_button = driver.find_element(By.XPATH, notifications_icon)
    notifications_button_img = notifications_button.get_attribute('src')[64:96]

    # This are the enabled and disabled images for notifications.
    # In earlier versions or newer versions of the Cisco Management Center this icons might or may not be different.

    if notifications_button_img == enabled_image:
        print('Disabling notifications!')
        print(notifications_button_img)
        notifications_button.click()
    elif notifications_button_img == disabled_image:
        print('Button is already disabled!')
        print(notifications_button_img)

    tasks_element.click()

    time.sleep(2)


# Your custom code goes in here
def my_function(driver: webdriver, manager: str, version: str, *args, **kwargs) -> None:
    '''
    Start your automation code on here.

    :param driver: The web browser driver.
    :param manager: The Address of the Manager/FMC.
    :param version: The version of FMC you are using.
    :return: None
    '''
    if manager.startswith('http'):
        driver.get('{}/platinum/ApplianceInformation.cgi'.format(manager))
    else:
        driver.get('https://{}/platinum/ApplianceInformation.cgi'.format(manager))


# The address of the manager you want to login to
MANAGER = '127.0.0.1'

# The version of FMC you are using
VERSION = '6.3.0'

# Login on the web interface
DRIVER = fmc_login(MANAGER, os.environ.get('USERNAME'), os.environ.get('PASSWORD'), VERSION)

# Disables the notificatiosn globally
disabled_notifications(DRIVER, VERSION)

# Run your custom function
my_function(DRIVER, MANAGER, VERSION)

# Logout of the web interface and quit everything gracefully
logout(DRIVER, MANAGER)
