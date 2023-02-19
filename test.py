import csv
import re
import time
from turtle import pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

    for index in range(len(open('data.csv').readlines())):

        print(index)
        # Get user information from CSV file
        address, city, state, owner = get_info_user('data.csv', index)
        print(address, city, state, owner)

        # Set up the web driver
        driver = setup_web_driver()

        # Navigate to the True People Search website
        driver.get("https://www.truepeoplesearch.com/")

        # Find the search box and enter the name you want to search for
        search_box_owner = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#id-d-n')))
        s_city_state = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#id-d-loc-name')))
        search_box_owner.send_keys(owner)
        s_city_state.send_keys(city+", "+state)

        # Submit the search by pressing enter
        search_box_owner.send_keys(Keys.RETURN)
        driver.implicitly_wait(20)

        # Wait for the search results to load
        num_results = int(driver.find_element(By.CSS_SELECTOR, 'div.record-count .col:first-child').text.split()[0])

        # i wanna found the number of results and then loop through them and get the links and then loop through them and get the info usually it's like this "1 record found for Brian Carman"
        if num_results >6:
            num_results=6

        results = driver.find_elements(By.CSS_SELECTOR, ".content-center .pt-3")[:num_results]
        col=driver.find_element(By.CSS_SELECTOR,".col")
        # ...
        
        links=[]
        for result in results:
            # data-detail-link="/details?name=Brian%20P%20Carman&citystatezip=Mundelein%20IL&rid=0xr"
            link="https://www.truepeoplesearch.com"+result.get_attribute("data-detail-link")        
            links.append(link)
            #since we only need 6 elements or less
            if len(links)>7:
                break
            


        # loop through each result and get the person's details
        for l,link in enumerate(links):
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
            # Open the input file in read mode
            # Open the input file in read mode
            # format the data so it would be like this
            # Brian Patrick Carman Age 51
            # (847) 830-1418 - Wireless
            # (847) 566-7405 - Landline
            # (847) 757-3847 - Wireless
            # Last lived there January 2021
            data = f'{name}\n{age}\n{add}\n{last_lived_address}\n{phone_numbers_str}'
            # Open the input file in read mode
            with open('result.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                #i wanna join the data so it will be in one column and also add the index of the row
                writer.writerow([index,data])
                
                #close the file
                file.close()


            #step 2 reverse address
            #in which i will need the address and the city and the state 
            driver.get("https://www.truepeoplesearch.com/")

            reverse_address = driver.find_element(By.CSS_SELECTOR, '#searchTypeAddress-d')
            reverse_address.click()
            driver.implicitly_wait(5)
            address_input = driver.find_element(By.CSS_SELECTOR, '#id-d-addr')
            s_city_state = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#id-d-loc-addr')))
            address_input.send_keys(address)
            s_city_state.send_keys(city+", "+state)
            address_input.send_keys(Keys.RETURN)
            # Submit the search by pressing enter
            driver.implicitly_wait(5)
            
        # Wait for the search results to load
        num_results = int(driver.find_element(By.CSS_SELECTOR, 'div.record-count .col:first-child').text.split()[0])

        # i wanna found the number of results and then loop through them and get the links and then loop through them and get the info usually it's like this "1 record found for Brian Carman"
        if num_results >6:
            num_results=6

        results = driver.find_elements(By.CSS_SELECTOR, ".content-center .pt-3")[:num_results]
        col=driver.find_element(By.CSS_SELECTOR,".col")
        # ...
        
        links=[]
        for result in results:
            # data-detail-link="/details?name=Brian%20P%20Carman&citystatezip=Mundelein%20IL&rid=0xr"
            link="https://www.truepeoplesearch.com"+result.get_attribute("data-detail-link")        
            links.append(link)
            #since we only need 6 elements or less
            if len(links)>7:
                break
            


        # loop through each result and get the person's details
        for li,link in enumerate(links):
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
            #for now put them in a text file seperated by a comma
            
            # Open the input file in read mode
            #i want to append the data next to the other pervious data
            # Open the output file in write mode
            data = f'{name}\n{age}\n{add}\n{last_lived_address}\n{phone_numbers_str}'
            # Open the input file in read mode
            with open('result.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                #i wanna join the data so it will be in one column and also add the index of the row
                writer.writerow([index,data])
                
                #close the file
                file.close()

            

    data_dict = {}

    #once done i need to process  it 
    with open('result.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            index = row[0]
            data = row[1:]
            if index not in data_dict:
                data_dict[index] = []
            data_dict[index].append(data)

    # # write the combined data to a new CSV file
    # with open('combined.csv', 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     for index, data_list in data_dict.items():
    #         combined_data = [index] + [', '.join(data) for data in data_list]
    #         writer.writerow(combined_data)


        
        #step 3 check the phone numbers 
        # Create a dictionary of area codes and their corresponding files
        area_codes = {
            '630': 'area_code/630.txt',
            '815': 'area_code/815.txt',
            '847': 'area_code/847.txt'
        }

        # Read the CSV file
        df = pd.read_csv('result.csv', header=None)

        # Define a function to check if a number is in the do-not-call list
        def is_on_do_not_call_list(number):
            for code in area_codes:
                with open(area_codes[code], 'r') as f:
                    if number in f.read().split('\n'):
                        return True
            return False

        # Define a function to apply the formatting to a row
        def format_row(row):
            # Check the area code and highlight the row in red if it's not in the list of area codes
            if str(row[5])[2:5] not in area_codes:
                return ['background-color: red'] * len(row)

            # Check if the number is in the do-not-call list and strike through the row if it is
            if is_on_do_not_call_list(row[5]):
                return ['text-decoration: line-through'] * len(row)

            # Make the row bold if the number is not in the do-not-call list
            return ['font-weight: bold'] * len(row)

        # Apply the formatting to the entire DataFrame
        df_styled = df.style.applymap(format_row, subset=pd.IndexSlice[:, [5]])

        # Export the styled DataFrame to HTML
        with open('output.html', 'w') as f:
            f.write(df_styled.render())
        
        driver.quit()

