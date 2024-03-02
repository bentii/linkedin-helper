import os
import pickle
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

load_dotenv()

def keywords_treatment(keywords):
    return keywords.replace(' ', '%20')

def search(driver):
    people = 0
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//ul[contains(@class, \"reusable-search__entity-result-list list-style-none\")]//button")))
        buttons = driver.find_elements(By.XPATH, '//ul[contains(@class, "reusable-search__entity-result-list list-style-none")]//span[contains(@class, "artdeco-button__text")]')
        for button in buttons:
            if 'Connect' in button.get_attribute('innerHTML'):
                content = button.find_element(By.XPATH, '../../../../div//a//span//span')
                print(content.text)
                button.click()
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@aria-label="Send now"]')))
                send_note = driver.find_element(By.XPATH, '//*[@aria-label="Send now"]')
                send_note.click()
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//ul[contains(@class, \"reusable-search__entity-result-list list-style-none\")]//button")))
                people += 1
    except TimeoutException:
        print("-------------------------------------------------------------------Error while trying to connect with people")
    return people

def main():
    keywords = input("Parameters to search for:")
    run = input("Number of pages to search:")
    run = int(run)

    webdriver_service = Service('/usr/bin/chromedriver')

    chrome_options = Options()
    # chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    print(f"Starting LinkedIn search process for {keywords}")
    try:
        driver.get("https://www.linkedin.com/login")

        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID,"username")))
            
        if driver.current_url != "https://www.linkedin.com/feed/":
            login(driver)
            save_cookies(driver)
        
        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "feed-identity-module__member-bg-image")))
            driver.get(f"https://www.linkedin.com/search/results/people/?keywords={keywords_treatment(keywords)}&origin=GLOBAL_SEARCH_HEADER")
        except TimeoutException:
            print("-------------------------------------------------------------------Error while loading the search")
            driver.quit()
            
        people = 0    
        people = search(driver)
        
        next_page = 2
        run_counter = 1
        while run_counter != run:
            try:
                driver.get(f"https://www.linkedin.com/search/results/people/?keywords={keywords_treatment(keywords)}&origin=GLOBAL_SEARCH_HEADER&page={next_page}")
                next_page += 1
                run_counter += 1
                people += search(driver)
            except TimeoutException:
                print("-------------------------------------------------------------------Error while trying to access the next page")
                driver.quit()
                break
    except WebDriverException:
        print("-------------------------------------------------------------------Error while accessing the website")
        driver.quit()
    finally:
        driver.quit()
        print(f"Connected with {people} people from {keywords}")

def login(driver):
    try:
        input_username = driver.find_element(By.ID,"username")
        input_username.send_keys(os.getenv("LINKEDIN_USERNAME"))
        input_password = driver.find_element(By.ID,"password")
        input_password.send_keys(os.getenv("LINKEDIN_PASSWORD"))
        submit_button = driver.find_element(By.CLASS_NAME,"from__button--floating")
        submit_button.click()
    except NoSuchElementException:
        print("-------------------------------------------------------------------Error while logging in")
        # driver.quit()

def save_cookies(driver):
    try:
        cookies = driver.get_cookies()
        with open("cookies.pkl", "wb") as file:
            pickle.dump(cookies, file)
    except IOError:
        print("-------------------------------------------------------------------Error while saving cookies")

if __name__ == "__main__":
    main()
