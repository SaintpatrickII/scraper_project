from selenium import webdriver
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import uuid
import json
from selenium.common.exceptions import NoSuchElementException
import boto3
import pandas as pd
from selenium import webdriver 
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
from sqlalchemy import create_engine
import urllib.request
import tempfile

class Webscraper:
    def __init__(self):
        self.link_list = []
        self.coin_image_completed = []
        self.friendly_id_list = []
        self.final_coin_details=[]
        self.webdriver_installer = chromedriver_autoinstaller.install()
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=800,600")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.addArguments("--disable-browser-side-navigation")
        chrome_options.addArguments("--disable-gpu")
        chrome_options.addArguments("start-maximized")
        #self.driver = webdriver.Chrome('/Users/paddy/Desktop/AiCore/scraper_project/chromedriver')
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver.get('https://coinmarketcap.com/')
        self.url = 'https://coinmarketcap.com/'
        self.next_page_string = '?page='
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        ENDPOINT = 'patrickcryptodbfinal.cycquey1wjft.us-east-1.rds.amazonaws.com' 
        USER =  'postgres'
        PASSWORD = 'postgres'
        PORT = 5432
        DATABASE = 'postgres'
        self.engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        self.client = boto3.client('s3')
        self.df = pd.read_sql_table('coin_data', self.engine)
        self.id_checker = list(self.df['friendly_id']) 


        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.cmc-cookie-policy-banner__close"))).click()
        sleep(10)

    """
    Initaliser:
    
    defines driver local location, creates
    empty lists to be used in webscraper &
    defines website to be webscraped, initilises 
    sqlalchemy engine for RDS transfer & sets up
    friendly_id to ensure no rescraping of data, 
    also clicks cookie banner
    """
    
    
    def individual_coin_path(self):
        
        sleep(2)
        coin_container = self.driver.find_element_by_xpath('//table[@class="h7vnx2-2 czTsgW cmc-table  "]')
        coin_list = coin_container.find_elements_by_xpath('./tbody/tr')
        return coin_list

    
    """
    Individual_coin_path:
    
    defines table on webpage which is
    to be iterated through to scrape 
    properties of various coins
    """


    def crypto_properties(self):
        coin_list = self.individual_coin_path()
        self.image_path = '/Users/paddy/Desktop/AiCore/Scraper_Project/Coin_Images'
        sleep(3)
        i = 1
        self.driver.execute_script("window.scrollBy(0, 50)")
        self.driver.execute_script("document.body.style.zoom='50%'")
        for i in range(len(coin_list)):
            try:
                full_coin_list= {
                    'uuid' : str(uuid.uuid4()),
                    'Name': coin_list[i].find_element_by_xpath('.//td[3]//a//p').text,
                    'Symbol' : coin_list[i].find_element_by_xpath('.//td[3]/div/a/div/div/div/p').text,
                    'Price' : coin_list[i].find_element_by_xpath('.//td[4]/div/a/span').text,
                    'Volume' :coin_list[i].find_element_by_xpath('.//td[8]/div/a/p').text,
                    'Market_cap' : coin_list[i].find_element_by_xpath('.//td//p/span[2]').text,
                    'Circulating_Supply' : coin_list[i].find_element_by_xpath('.//td[9]//div/div[1]/p').text
                }
            except NoSuchElementException:
                    continue
            friendly_id_con = coin_list[i].find_element_by_xpath('.//td[3]/div/a')
            friendly_id = friendly_id_con.get_attribute('href')
            friendly_id_split = friendly_id.split('/')[-2]
            self.friendly_id_list.append(friendly_id_split)
            img = coin_list[i].find_element_by_class_name('coin-logo')
            src = img.get_attribute('src')
            full_coin_list['image'] = src
            full_coin_list['friendly_id'] = friendly_id_split
            coin_list = self.individual_coin_path()
            print(full_coin_list)
            self.driver.execute_script("window.scrollBy(0, 50)")
            if friendly_id in self.friendly_id_list:
                continue
            else:
                self.final_coin_details.append(full_coin_list)
            if i == 100:
                self.save_to_json_final()
                return full_coin_list()
            

    """
    crypto_properties:
    
    this sets up the dictionary with all of 
    the coins attributes, also is responsible for 
    setting the friendly id to stop rescraping
    & scrolls the page as the scraper collects
    results
    """


    def save_to_json_final(self):
            final_coin_list = []
            for coin in self.final_coin_details:
                if coin not in final_coin_list:
                    final_coin_list.append(coin)
            
            complete_full_coin_list = final_coin_list
            with open('coins_data.json', encoding='utf-8', mode='w') as file:
                json.dump(complete_full_coin_list, file, ensure_ascii=False, indent=4)


    """
    save_to_json:
    
    responsible for ensuring no duplicate 
    results saved & all coins saved to
    easy to read json format
    """


    def page_iterator(self, no_of_pages):
        sleep(5)
        element = self.driver.find_elements_by_xpath("//a[@aria-label='Next page']")
        page = 1
        while page <= no_of_pages:
            self.crypto_properties()
            self.driver.execute_script("document.body.style.zoom='100%'")
            next_page_button = element[1]
            sleep(3)
            next_page_button.click()
            page += 1
            print(f'page {page} is completed')
            if page == no_of_pages:
                return 


    """
    page_iterator:
    
    responsible for iterating
    webscraper through first 10
    pages of website, alongside 
    saving results once webscraper 
    finishes
    
    input: no_of_pages = int
    """

    def split_image_url(self):
        self.image_link = []
        self.image_uuid = []
        for j in self.final_coin_details:
            dict_values = j.values()
            v_image_link = list(dict_values)[7]
            v_uuid = list(dict_values)[0]
            self.image_link.append(v_image_link)
            self.image_uuid.append(v_uuid)
        print(self.image_link)
        print(self.image_uuid)


    '''
    Split_image_url:
    
    This method collects the image
    url from the saved json object &
    formats it to be uploaded to the s3 bucket'''


    def upload_image_jpeg(self):
        self.split_image_url()
        v_image_link = self.image_link
        v_uuid= self.image_uuid
        with tempfile.TemporaryDirectory() as tmpdict:
            for i in range(len(self.image_link)):
                urllib.request.urlretrieve(v_image_link[i], tmpdict + f'{v_uuid[i]}.jpg')
                self.client.upload_file(tmpdict + f'{v_uuid[i]}.jpg', 'patrickcryptobucketfinal', f'{v_uuid[i]}.jpg')
            return


    '''
    upload_image_jpeg:

    Using a temporary dictionary,
    iterates throught the image url's 
    sending them to the AWS S3 bucket in
    jpeg format labelled with the same
    uuid as the json data belonging to that coin 
    '''
    
    
    def data_to_sql(self):
        with open('./coins_data.json', 'r') as filename:
            df_coins = json.load(filename)
        df = pd.DataFrame(df_coins)
        df.columns = df.columns.str.lower()
        self.engine.connect()
        df.to_sql('coin_data', con=self.engine, if_exists='replace')
        pd.read_sql_query('''SELECT DISTINCT coin_data.Name From coin_data;''', self.engine)
        print('duplicate values have been removed')
        
        
    '''
    data_to_sql:
    
    turns json into pandas df &
    imports that to postresql, checks 
    with postresql that no duplicates exist using DISTINCT
    SQL function
    '''


if __name__ == '__main__':
    public_webscraper = Webscraper()
    public_webscraper.page_iterator(2)
    public_webscraper.upload_image_jpeg()
    public_webscraper.save_to_json_final()
    public_webscraper.data_to_sql()


    '''
    Main initiliser:

    the if statement infers 
    that this file is the main file 
    being run instead of importing from 
    a seperate module as this is true it 
    will initilise both our classes & run them 
    sequentially
    '''