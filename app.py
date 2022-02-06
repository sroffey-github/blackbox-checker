from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from pyvirtualdisplay import Display
from twilio.rest import Client
import datetime
import os

load_dotenv()

# import selenium libraries

# simulate display for selenium to work
#display = Display(visible=0, size=(800, 600))
#display.start()

email = os.getenv('EMAIL')
passwd = os.getenv('PASSWORD')

url = 'https://boxins.tescobank.com/accountmanagement/dist/html/#/auth/login'


options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(executable_path=f'{os.getcwd()}/chromedriver', options=options)

driver.get(url)

driver.implicitly_wait(15) # wait 15seconds for page to load

# accept cookies etc. (added try except incase this is removed)
try:
    driver.find_element_by_css_selector('#ensCloseBanner').click()
except:
    pass
try:
    driver.find_element_by_css_selector('body > div.gw-modal.gw-fade.gw-modal_animation_.in > div > div.gw-modal-footer.ng-scope > button').click()
except:
    pass

# login page
email_input = driver.find_element_by_css_selector('body > div.ng-scope > and-auth-base > div > main > div > div > section > and-lock-login > div:nth-child(1) > div:nth-child(2) > div > div > form > div:nth-child(1) > div > div > ng-transclude > input')
passwd_input = driver.find_element_by_css_selector('body > div.ng-scope > and-auth-base > div > main > div > div > section > and-lock-login > div:nth-child(1) > div:nth-child(2) > div > div > form > div:nth-child(2) > div > div > ng-transclude > input')

email_input.send_keys(email)
passwd_input.send_keys(passwd)

login_btn = driver.find_element_by_css_selector('body > div.ng-scope > and-auth-base > div > main > div > div > section > and-lock-login > div:nth-child(1) > div:nth-child(2) > div > div > form > gw-branding-segmentation > gw-segmentation-option:nth-child(1) > div > button')
login_btn.send_keys(Keys.ENTER)

# main page
bonus_miles_btn = WebDriverWait(driver, 20).until(
EC.element_to_be_clickable((By.CSS_SELECTOR, "body > div.ng-scope > div.and-d-flex.and-flex-column.ng-scope > header > div > div.and-header-nav-wrapper > div > div > div > div.and-navigation-left > div:nth-child(2)")))
bonus_miles_btn.click()

# table
table_body = driver.find_element_by_css_selector('body > div.ng-scope > div.and-d-flex.and-flex-column.ng-scope > div > div.and-flex-expand.and-d-flex.and-flex-column > div > div > div > div.and-policy-context-right.ng-scope > div > div > div.ng-scope > div:nth-child(3) > div > div > div > div > table > tbody')

scores = table_body.text

# ------------------- #
# Notify Function
# ------------------- #

account_sid = os.getenv('ACCOUNT_SID')
auth_token  = os.getenv('AUTH_TOKEN')
twilio_number = os.getenv('NUMBER')

def log(msg):
    with open('logs/log.txt', 'a') as f:
        f.write(f'[{datetime.datetime.now()}] {msg}' + '\n')

def send(msg):

    client = Client(account_sid, auth_token)

    NUMBERS = [os.getenv('NUMBER')]

    for number in NUMBERS:

        message = client.messages.create(
            to=number,
            from_=twilio_number,
            body=msg)

        log(f'[NEW REPORT] New Report Detected')

# ---------------------------------- #
# calculate if there is a new report
# ---------------------------------- #

months = {
    'Jan':'01',
    'Feb':'02',
    'Mar':'03',
    'Apr':'04',
    'May':'05',
    'Jun':'06',
    'Jul':'07',
    'Aug':'08',
    'Sep':'09',
    'Oct':'10',
    'Nov':'11',
    'Dec':'12',
}

text = '''
03 Dec 21 - 02 Jan 22 100
03 Nov 21 - 02 Dec 21 100
Click to show score above
03 Oct 21 - 02 Nov 21 100
Click to show score above
03 Sep 21 - 02 Oct 21 100
Click to show score above
03 Aug 21 - 02 Sep 21 100
Click to show score above
03 Jul 21 - 02 Aug 21 100
Click to show score above
03 Jun 21 - 02 Jul 21 100
Click to show score above
'''

split_text = text.strip().split('\n')

try:
    while True:
        split_text.remove('Click to show score above')
except ValueError:
    pass

most_recent = split_text[0]
most_recent_split = most_recent.split(' ') # example: ['03', 'Dec', '21', '-', '02', 'Jan', '22', '100']

day = int(most_recent_split[-4]) # 4th last item in list
month = int(months[most_recent_split[-3]]) # 3rd last item in list
year = int("20" + most_recent_split[-2]) # 2nd last item in list
score = most_recent_split[-1] # 1st last item in list

most_recent_date = datetime.datetime(year, month, day)

current_day = int(datetime.date.strftime(datetime.datetime.now(), "%d"))
current_month = int(datetime.date.strftime(datetime.datetime.now(), "%m"))
current_year = int(datetime.date.strftime(datetime.datetime.now(), "%Y"))

current_date = datetime.datetime(current_year, current_month, current_day)

if most_recent_date >= current_date:
    # new report
    send(f'Tesco Blackbox Login\n\nNew Report Detected: "Date: {str(most_recent_date)} Score: {score}"')
else:
    # no new report
    print('[-] No New Report')
