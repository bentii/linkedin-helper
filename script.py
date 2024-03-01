import argparse
import os
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser(description="Busca no LinkedIn")
parser.add_argument('keywords', type=str, help="Palavras-chave para a busca")
parser.add_argument('run', type=int, help="Numero de paginas para buscar")

args = parser.parse_args()

webdriver_service = Service('/usr/bin/chromedriver')

chrome_options = Options()
# chrome_options.add_argument('--headless')

driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

pessoas = 0
run_counter = 0

def keywords_treatment(keywords):
    return keywords.replace(' ', '%20')

def search():
    global pessoas
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
                pessoas += 1
    except Exception as e:
        pass


print(f"Iniciando processo de busca no LinkedIn por {args.keywords}")
try:
    driver.get("https://www.linkedin.com/login")

    # try:
    #     with open("cookies.pkl", "rb") as file:
    #         cookies = pickle.load(file)
    #         for cookie in cookies:
    #             cookie['domain'] = '.linkedin.com'
    #             try:
    #                 driver.add_cookie(cookie)
    #                 print('cukiiii')
    #             except Exception as e:
    #                 print("-------------------------------------------------------------------Erro ao adicionar os cookies")
    #                 print(e)
    # except FileNotFoundError:
    #     print("-------------------------------------------------------------------Sem arquivo cookies.")
    # time.sleep(2)
    # driver.refresh()
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID,"username")))
        
    if driver.current_url != "https://www.linkedin.com/feed/":
        
        try:
            input_username = driver.find_element(By.ID,"username")
            input_username.send_keys(os.getenv("LINKEDIN_USERNAME"))
            input_password = driver.find_element(By.ID,"password")
            input_password.send_keys(os.getenv("LINKEDIN_PASSWORD"))
            submit_button = driver.find_element(By.CLASS_NAME,"from__button--floating")
            submit_button.click()
        except Exception as e:
            print("-------------------------------------------------------------------Erro ao logar")
            print(e)
            # driver.quit()
            
        try:
            cookies = driver.get_cookies()
            with open("cookies.pkl", "wb") as file:
                pickle.dump(cookies, file)
        except Exception as e:
            print("-------------------------------------------------------------------Erro ao salvar os cookies")
            print(e)
    
    # try:
    #     WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "home_children_button")))
    #     if driver.current_url == "https://www.linkedin.com/checkpoint/challenge/":
    #         print("Captcha detectado")
    # except Exception as e:  
    #     print("-------------------------------------------------------------------Erro no captcha")
    #     print(e)
    #     driver.quit()
        
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "feed-identity-module__member-bg-image")))
        driver.get("https://www.linkedin.com/search/results/people/?keywords={keywords}&origin=GLOBAL_SEARCH_HEADER".format(keywords=(args.keywords)))
    except Exception as e:
        print("-------------------------------------------------------------------Erro ao carregar a busca")
        print(e)
        driver.quit()
        
    try:
        search()
    except Exception as e:
        print("-------------------------------------------------------------------Erro ao tentar conectar com pessoas")
        print(e)
        driver.quit()
        
    try:
        next_page = 2
        while run_counter != args.run:
            driver.get("https://www.linkedin.com/search/results/people/?keywords={keywords}&origin=GLOBAL_SEARCH_HEADER&page={next_page}".format(keywords=args.keywords, next_page=next_page))
            next_page += 1
            run_counter += 1
            search()
    except Exception as e:
        print("-------------------------------------------------------------------Erro ao tentar acessar a próxima página")
        print(e)
        driver.quit()
except Exception as e:
    print("-------------------------------------------------------------------Erro ao acessar o site")
    print(e)
    driver.quit()
finally:
    driver.quit()
    print(f"Conectado com {pessoas} pessoas de {args.keywords}")
