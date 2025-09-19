from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import time
import datetime
import requests
import json
import os
import pickle
import io
from flask import Flask, request, jsonify
import cloudinary
import cloudinary.uploader
import threading

app = Flask(__name__)
load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("cloud_name"),
    api_key=os.getenv("api_key"),
    api_secret=os.getenv("api_secret")
)

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
    

def upload_json(data):
    # Convert to string and then to bytes
    json_str = json.dumps(data, indent=2)
    json_bytes = io.BytesIO(json_str.encode('utf-8'))
    print('Start Uploading')
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    # os.makedirs("top-gainers-losers", exist_ok=True)
    # filename = f"top-gainers-losers/top-gainers-losers-{timestamp}.json"
    filename = f"top-gainers-losers-{timestamp}.json"
    # Upload to Cloudinary as a raw file
    result = cloudinary.uploader.upload(
        json_bytes,
        type="private",
        resource_type="raw",
        filename = filename,
        folder = "top-gainers-losers",
        overwrite=True,
        use_filename=True,
        unique_filename=False
    )
    print(result)
    print(filename)
    print("upload Done")
    return jsonify({
        "uploaded": True
    })

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
                  # print(data)
                  print(f'{x} and {check} Done.')  # Print the data or process it as needed
                  check +=1
    
              else:
                  print(f"Failed to fetch data. Status Code: {response.status_code}")
          except Exception as e:
              print(f"An error occurred: {e}")
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    # os.makedirs("top-gainers-losers", exist_ok=True)
    filename = f"top-gainers-losers/top-gainers-losers-{timestamp}.json"
    if len(all_data) >0:
        
        # with open(filename, "w", encoding="utf-8") as f:
        #     json.dump(all_data, f, indent=2)
        upload_json(all_data)
        print(f"📁 Data saved to: {filename}")
        # print(f"📁 Data saved to: {filename}")
    print("Scrape job finished.")

@app.route('/run-scrape')
def run_scraper():
    # Run scraping in a separate thread to avoid timeout on Replit
    # threading.Thread(target=scrape_nse_data).start()
    scrape_nse_data()
    return "Scraper started!"

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
