import csv
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from capmonster_python import RecaptchaV2Task

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
    print(address, city, state, owner)

    # Set up the web driver
    driver = setup_web_driver()

    # Navigate to the True People Search website
    driver.get("https://www.truepeoplesearch.com/")

    # Find the search box and enter the name you want to search for
    search_box_owner = driver.find_element(By.CSS_SELECTOR, '#id-d-n')
    s_city_state=driver.find_element(By.CSS_SELECTOR,'#id-d-loc-name')
    search_box_owner.send_keys(owner)
    s_city_state.send_keys(city+", "+state)

    # Submit the search by pressing enter
    search_box_owner.send_keys(Keys.RETURN)
    # i want that once the html is rendered to stop loading cuz there is some google analytics type thing going on that slows down the scraping how do i do that
    # driver.set_page_load_timeout(10)






    # if driver.find_element(By.CLASS_NAME,"h-captcha"):
    #     captcha_element = driver.find_element(By.CLASS_NAME,"h-captcha")
        
    #     # Extract the sitekey from the element
    #     sitekey = captcha_element.get_attribute("data-sitekey")
    #     print("ss",sitekey)
    #     # Initialize CapMonster with your API key and create a RecaptchaV2Task object
    #     client_key = '207440ed3bd9bc89d821c16d714fd2b3'
    #     # task = RecaptchaV2Task(site_key='6LfPJiMTAAAAAPGMGJX9XnL2QCRINjOq_Swcrv_0', url='https://www.truepeoplesearch.com/')
    #     task = RecaptchaV2Task(client_key)
    #     # Solve the captcha using CapMonster and get the taskId
    #     task_id  =task.create_task('https://www.truepeoplesearch.com/',sitekey )
    #     time.sleep(10)
        
    #     # Check the status of the task until it is completed
    #     while True:
    #         response = task.get_task_result(task_id)
    #         if response.get('status') == 'ready':
    #             break
    
        # there is no captcha u need to get the first 6 results and
        
    # Wait for the search results to load
    # get the first 6 results
    print("berrrrrrrrrrrrr")
    num=driver.find_element(By.CSS_SELECTOR,".col")
    print(num.text)
    results = driver.find_elements(By.CSS_SELECTOR, ".content-center .pt-3")[:6]
    #so what i want to do is to scrape the first 6 links if they exist if not what's less than 6

    links=[]
    print(results)
    for result in results:
        # data-detail-link="/details?name=Brian%20P%20Carman&citystatezip=Mundelein%20IL&rid=0xr"
        link="https://www.truepeoplesearch.com"+result.get_attribute("data-detail-link")        
        links.append(link)
        #since we only need 6 elements or less
        if len(links)>7:
            break
        

    print(links)

    # loop through each result and get the person's details
    for link in links:
        driver.get(link)
        driver.implicitly_wait(5)
        name=driver.find_element(By.CSS_SELECTOR,".h2").text
        age=driver.find_element(By.CSS_SELECTOR,".content-value").text
        personal_info=driver.find_element(By.CSS_SELECTOR,"#personDetails").text
        add=driver.find_element(By.CSS_SELECTOR,".olnk").text
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
        print(name,age,add,last_lived_address,phone_numbers_str)
        #save all that data  in csv in one box for each link
        with open('people.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([name,age,add,last_lived_address,phone_numbers_str])




        


    # Close the web driver
    driver.quit()
