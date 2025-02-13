from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from upload_gdrive import upload_to_drive
import calendar
import pandas as pd
import time

# Set your login credentials here
USERNAME = ""  # Replace with actual username
PASSWORD = "" # Replace with actual password

# Set the start date and end date
today = datetime.today()
today_be = today.replace(year=today.year + 543)
if today.day <= 15:
    start_date = today_be.replace(day=1)
    end_date = today_be.replace(day=15)
else:
    start_date = today.replace(day=16)
    end_date = today.replace(day=calendar.monthrange(today.year, today.month)[1])

# Set the output path
start_dt_file_fm = start_date.strftime("%Y%m%d")
end_dt_file_fm = end_date.strftime("%Y%m%d")
output_filename = f"C:_{start_dt_file_fm}_{end_dt_file_fm}.xlsx"

# Set Google Drive folder
GDRIVE_FOLDER = ""

# Path to your Chrome WebDriver (Update this path if necessary)
chrome_options = webdriver.ChromeOptions()

# Initialize Selenium WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Open the website
url = ""
driver.get(url)

# Wait for elements to load
time.sleep(3)

# Click the "Agree" button
try:
    agree_button = driver.find_element(By.CLASS_NAME, "accept-agreement")
    agree_button.click()
    time.sleep(2)  # Wait for the login page to load
except Exception as e:
    print("Error clicking the agreement button:", e)

# Enter username
username_input = driver.find_element(By.ID, "username_txt")
username_input.clear()
username_input.send_keys(USERNAME)

# Enter password
password_input = driver.find_element(By.ID, "password_txt")
password_input.clear()
password_input.send_keys(PASSWORD)

# Press Enter to log in
password_input.send_keys(Keys.RETURN)
time.sleep(2)  # Wait for login process

# Click the submit button (instead of pressing Enter)
try:
    advance_search_button = driver.find_element(By.CLASS_NAME, "advance-search")
    advance_search_button.click()
    time.sleep(5)  # Wait for login to process
except Exception as e:
    print("Error clicking the Advance Search button:", e)

# Select the first dropdown (id="ddl_search_case_organization") with value "3"
select_org = Select(driver.find_element(By.ID, "ddl_search_case_organization"))
select_org.select_by_value("3")  # Selecting organization 3
time.sleep(1)

# Select the second dropdown (id="ddl_search_case_organizationx") with value "302"
select_orgx = Select(driver.find_element(By.ID, "ddl_search_case_organizationx"))
select_orgx.select_by_value("302")  # Selecting sub-organization 302
time.sleep(1)

# Select date from the datepicker (id="hasDatepicker")
date_from_input = driver.find_element(By.ID, "txt_search_date_from")
date_from_input.clear()
date_from_input.send_keys(start_date.strftime("%d/%m/%Y"))  # Start date (in Buddhist Calendar format)
date_from_input.send_keys(Keys.RETURN)
time.sleep(1)

date_to_input = driver.find_element(By.ID, "txt_search_date_to")
date_to_input.clear()
date_to_input.send_keys(end_date.strftime("%d/%m/%Y"))  # End date (same as start date)
date_to_input.send_keys(Keys.RETURN)
time.sleep(1)

# Click the "Search" button (adjust selector as needed)
try:
    # Wait for the search button to be clickable
    search_button = driver.find_element(By.ID, "button_advance_search")
    
    # Scroll to the element (if it's out of view)
    driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
    time.sleep(1)  # Allow time for scrolling
    
    # Try clicking using JavaScript (for dynamic buttons)
    driver.execute_script("arguments[0].click();", search_button)
    
    time.sleep(10)  # Wait for results to load
except Exception as e:
    print("Error clicking the search button:", e)

# Extract table data
all_data = []
while True:
    try:
        # Get page source after table loads
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Find the table inside <div class="datagrid-case">
        table_div = soup.find("div", class_="datagrid-case")
        if not table_div:
            print("Table not found!")
            break

        # Extract headers (only once)
        if not all_data:
            thead = table_div.find("thead")
            headers = [th.text.strip() for th in thead.find_all("th")]

        # Extract table body rows
        tbody = table_div.find("tbody")
        table_rows = tbody.find_all("tr")

        # Check if the table shows "no more data"
        if not table_rows:
            break

        # Extract row data from current page
        for row in table_rows:
            cells = row.find_all("td")
            row_data = [cell.text.strip() for cell in cells]
            print(row_data)

            # Ensure the row is not empty before adding
            if any(row_data):
                all_data.append(row_data)

        # Try to find the "Next" button for pagination
        next_button = driver.find_element(By.CLASS_NAME, "next-page.page-control")
        # Scroll to the element (if it's out of view)
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(10)  # Wait for new data to load

    except Exception as e:
        print("Error extracting table data or pagination:", e)
        break

# Close the browser
driver.quit()

# Convert to DataFrame and display
df = pd.DataFrame(all_data, columns=headers)
df.to_excel(output_filename)
print(df.head(100))

upload_to_drive(output_filename, GDRIVE_FOLDER)
