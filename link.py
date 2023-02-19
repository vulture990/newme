import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from capmonster_python import RecaptchaV2Task
import re

def get_info_user(csv_file, index):
    """
    Retrieves address, city, state, and owner information from a CSV file based on a zero-based index.

    Args:
        csv_file (str): The path to the CSV file.
        index (int): The zero-based index of the row to retrieve.

    Returns:
        A tuple containing the address, city, state, and owner information from the specified row, or None if the index is out of range.
    """
    with open(csv_file, 'r', newline='') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # skip header row if exists
        for i, row in enumerate(reader):
            if i == index:
                return row[3], row[4], row[5], row[13]  # assuming address, city, state, and owners
    return None  # index out of range


def setup_web_driver():
    """
    Sets up a Chrome web driver with custom options.

    Returns:
        A configured Chrome web driver.
    """
    # Set up the web driver options
    options = Options()

    # Set the user agent to a common Chrome user agent
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36')

    # Set the language to English (United States)
    options.add_argument('--lang=en-US')

    # Set the window size to 1366x768
    options.add_argument('--window-size=1366,768')

    # Set the data directory to avoid detection
    options.add_argument('--user-data-dir=/path/to/chrome/profile')
    service = Service(ChromeDriverManager().install())

    # Set up the web driver (you may need to download a driver for your specific browser)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def one_difference(str1, str2):
    if len(str1) != len(str2):
        # If the strings have different lengths, they can't have only one difference
        return False
    
    diffs = 0
    for i in range(len(str1)):
        if str1[i] != str2[i]:
            # If there is more than one difference, return "no"
            diffs += 1
            if diffs > 1:
                return False
    
    # If there is exactly one difference, return "yes"
    return True






if __name__ == '__main__':

    # Set up CapMonster client

    # Get user information from CSV file
    address, city, state, owner = get_info_user('data.csv', 0)
    

    # Set up the web driver
    driver = setup_web_driver()

    # Navigate to the True People Search website

    driver.set_page_load_timeout(10)

    try:
        # navigate to the URL
        driver.get("https://www.truepeoplesearch.com/details?name=Brian%20P%20Carman&citystatezip=Mundelein%2C%20IL&rid=0x0")
    except :
        # handle timeout exception
        print('Page took too long to load')

    name=driver.find_element(By.CSS_SELECTOR,".h2").text
    age=driver.find_element(By.CSS_SELECTOR,".content-value").text
    personal_info=driver.find_element(By.CSS_SELECTOR,"#personDetails").text
    add=driver.find_element(By.CSS_SELECTOR,".olnk").text
    # extract phone numbers sometimes there is no phone numbers
    # extract phone numbers sometimes there is no phone numbers
    try:
        phone_numbers = re.findall(r'(\(\d{3}\)\s\d{3}-\d{4})\s*-\s*(\w+)', personal_info)
        phone_numbers_str = '\n'.join([f'{num[0]} - {num[1]}' for num in phone_numbers])
    except:
        phone_numbers_str = 'No phone numbers listed'
    
    if one_difference(add[:len(address)], address) or add[:len(address)]==address:
        #meaning it's the current address 
        last_lived_address=""
    else:
        pattern = r"\((\w{3} \d{4}) - (\w{3} \d{4})\)"
        addresses = re.findall(pattern, personal_info)

        if addresses:
            last_lived_address = addresses[0][-1]
        else:
            last_lived_address = "No date listed"

    # Print the final output
    print(last_lived_address)
    print(f'{name} {age}')
    print(phone_numbers_str)
    print(address)
    driver.quit()