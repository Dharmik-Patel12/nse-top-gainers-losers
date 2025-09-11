from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import datetime
import time
from datetime import datetime
import requests
import json
import os
import pickle
import io
# from flask import Flask
# import threading

# app = Flask(__name__)


def get_cookies():
    options = Options()
    # options.add_argument("headless")  # run in headless mode if you want
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    options.add_argument("--headless")  # Headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-debugging-port=9222")
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.nseindia.com/market-data/top-gainers-losers")

    time.sleep(5)  # Wait for the page and cookies to load

    # Extract cookies from Selenium
    selenium_cookies = driver.get_cookies()
    # print(selenium_cookies)
    driver.quit()

    # Convert cookies to requests format
    cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
    return cookies

def scrape_nse_data():
    print("Starting scrape job...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.nseindia.com/market-data/top-gainers-losers",
        "Origin": "https://www.nseindia.com",
        "Connection": "keep-alive"
    }
    Category = ['gainers','loosers'] #Do Not change sequnce
    
    check = 0
    # all_data = []
    while True:
        if check == len(Category):
            break
        else:
            check = 0
        global all_data
        all_data = {}
        cookies = get_cookies()
        for x in Category:
            # URL for the API
          api_url = "https://www.nseindia.com/api/live-analysis-variations?index=" + x
    
          # Send the request
          try:
              # session = requests.Session()
              # # Make an initial request to obtain necessary cookies
              # session.get("https://www.nseindia.com", headers=headers)
              # response = session.get(url, headers=headers)
              response = requests.get(api_url, headers=headers, cookies=cookies)
    
              # Check if the request was successful
              if response.status_code == 200:
                  data = response.json()
                  # all_data.append(data)
                  all_data[x] = data
                  print(f'{x} and {check} Done.')  # Print the data or process it as needed
                  check +=1
    
              else:
                  print(f"Failed to fetch data. Status Code: {response.status_code}")
          except Exception as e:
              print(f"An error occurred: {e}")
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    os.makedirs("top-gainers-losers", exist_ok=True)
    filename = f"top-gainers-losers/top-gainers-losers-{timestamp}.json"
    if len(all_data) >0:
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2)
        
        print(f"📁 Data saved to: {filename}")
    print("Scrape job finished.")

# @app.route('/run-scrape')
# def run_scraper():
#     # Run scraping in a separate thread to avoid timeout on Replit
#     threading.Thread(target=scrape_nse_data).start()
#     return "Scraper started!"
print('Check')
if __name__ == "__main__":
    scrape_nse_data()
    # app.run(host="0.0.0.0", port=8080)


# from flask import Flask
# import threading

# app = Flask(__name__)

# def scrape_job():
#     # Your scraping code here
#     print("Scraping started...")
#     # do scraping
#     print("Scraping finished!")

# @app.route('/run-scrape')
# def run_scrape():
#     threading.Thread(target=scrape_job).start()
#     return "Scrape job started!"

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8080)
