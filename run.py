import csv
import json
import os
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def load_credentials(filename):
    with open(filename, 'r') as file:
        credentials = json.load(file)
    return credentials


def convert_csv(user_info):
    # Specify the path for the new CSV file
    csv_file_path = f"{user_info['username']}_following.csv"

    # Open the file in write mode
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write user information
        writer.writerow(["username", user_info["username"]])        
        # Write a blank row followed by the followers header
        writer.writerow([])
        writer.writerow(["following"," "],)
        
        # Write each follower on a new row
        for following in user_info["following"]:
            writer.writerow([following," "])
    print(f"[Info] - CSV file created at {os.path.abspath(csv_file_path)}")


def login(bot, username, password):
    bot.get('https://www.instagram.com/accounts/login/')
    time.sleep(1)

    # Check if cookies need to be accepted
    try:
        element = bot.find_element(By.XPATH, "/html/body/div[4]/div/div/div[3]/div[2]/button")
        element.click()
    except NoSuchElementException:
        print("[Info] - Instagram did not require to accept cookies this time.")

    print("[Info] - Logging in...")
    username_input = WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
    password_input = WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

    username_input.clear()
    username_input.send_keys(username)
    password_input.clear()
    password_input.send_keys(password)

    login_button = WebDriverWait(bot, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    login_button.click()
    time.sleep(10)


def scrape_following(bot, username, user_input):
    bot.get(f'https://www.instagram.com/{username}/')
    
    # time.sleep(3.5)
    # post_count = 0
    # followers = 0
    # following = 0
    # try:
    #     post_count = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@class="_aacl _aacp _aacw _aad6 _aade"]')))
    #     followers = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@class="_ac2a"]')))
    #     following = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@class="_ac2a"]')))
    # except Exception as e:
    #     print(e)
    
    time.sleep(3.5)
    WebDriverWait(bot, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/following')]"))).click()
    time.sleep(2)
    print(f"[Info] - Scraping following for {username}...")
    users = set()
    while len(users) < user_input:
        following = bot.find_elements(By.XPATH, "//a[contains(@href, '/')]")

        for i in following:
            # print(i.get_attribute('href'))
            if i.get_attribute('href'):
                users.add(i.get_attribute('href').split("/")[3])
            else:
                continue

        ActionChains(bot).send_keys(Keys.END).perform()
        time.sleep(1)
    return {
        "username": username,
        "following": list(users)
    }


def scrape():
    credentials = load_credentials('credentials.json')

    username=credentials["username"]
    password=credentials["password"]

    max_limit_of_following_to_scrape = credentials["max_limit_of_following_to_scrape"]

    usernames_to_scrape = credentials["usernames_to_scrape"]
    print(username, password, max_limit_of_following_to_scrape, usernames_to_scrape)

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument("--log-level=3")
    mobile_emulation = {
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/90.0.1025.166 Mobile Safari/535.19"}
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    bot = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    login(bot, username, password)

    for user in usernames_to_scrape:
        user = user.strip()
        convert_csv(scrape_following(bot, user, max_limit_of_following_to_scrape))
    bot.quit()


if __name__ == '__main__':
    TIMEOUT = 15
    scrape()
