from operator import contains
from tkinter import Image
import unittest
# from Crypto_Webscraper import Webscraper
import json
# from selenium import webdriver
#from Scraper_Project import coins.json


class TestWebscraper(unittest.TestCase):
    def setUp(self):
        with open('../Scraper_Project/coins.json', mode='r') as f:
            self.coins_json_in_list = json.load(f)
        self.coins_json = self.coins_json_in_list

        with open('../Scraper_Project/coins_images.json', mode='r') as f:
            self.image_list = json.load(f)   
    

    def parse(filename):
        filename = '../Scraper_Project/coins.json'
        try:
            with open(filename) as f:
                return json.load(f)
        except ValueError as e:
            print('invalid json: %s' % e)
            return None


    def test_coins_json_list_of_dict(self):
        self.assertIsInstance(self.coins_json, list)
        print('coins.json is a list')
        for k in self.coins_json:
            self.assertIsInstance(k, dict)
        print('coins.json has a dictionaries inside the lists')

    def test_coins_images_list_of_dict(self):
        self.assertIsInstance(self.image_list, list)
        print('image_list is a list')
        for k in self.image_list:
            self.assertIsInstance(k, dict)
        print('image_list has a dictionaries inside the lists')


    def test_keys(self):
        for k in self.coins_json:
            keys = k.keys()
            keys_iterable = list(keys)
            self.assertSetEqual(set(keys_iterable), set(["uuid", "Name", "Symbol", "Price",  "Volume", "Market_cap", "Circulating_Supply"]))
        print('coins.json has the correct keys')


    def test_is_images_list(self):
        dict_in_list = self.image_list
        for i in dict_in_list:
            v = i.values()
            v_names = list(v)[1]
            v_img_url = list(v)[2]
            self.assertIsInstance(v_names and v_img_url, str)
            self.assertEqual(v_img_url[0:51], 'https://s2.coinmarketcap.com/static/img/coins/64x64')
        print('images have the correct url & names and url in string format ')


    def tearDown(self):
        pass
    

if __name__ == '__main__':
    #testing = unittest.TestLoader().loadTestsFromTestCase(WebscraperTestCase)
    unittest.main(verbosity=2, exit=True)
    
    