from selenium import webdriver
from random import uniform
from time import sleep
from bs4 import BeautifulSoup as bs
from dataclasses import dataclass

import selenium.webdriver.firefox.webdriver as firefoxwd
import pandas as pd

@dataclass
class IdealistaQuery: 
    """ Query to submit to Idealista to obtain a listing of ads. """

    district: str
    neighbourhood: str
    max_price: int

    def get_idealista_path(self):
        """ URL to fetch to get the first page of results corresponding to the given query. """

        return f"https://www.idealista.com/venta-viviendas/barcelona/{self.district}/{self.neighbourhood}/con-precio-hasta_{self.max_price}/"


class IdealistaScraper:
    """ Scrapes ads from Idealista. """

    house_state = {
        'Segunda mano/buen estado': 'second_hand',
        'Segunda mano/para reformar': 'need_renovation',
        'Promoción de obra nueva': 'new'
    }

    query: IdealistaQuery
    driver: firefoxwd.WebDriver


    def __init__(self, query: IdealistaQuery):
        self.query = query
        self.driver = webdriver.Firefox()


    def get_result_page_url(self, page: int):
        """ Get the `page`-th results page url for the current query. """

        if not (1 <= page <= 100):
            raise ValueError(f"page should be between 1 and 100, you passed {page}")

        path = self.query.get_idealista_path()

        if page == 1:
            return path

        return f"{path}pagina-{page}.htm"


    def get_result_urls(self):
        """ Gets a list of urls for all ads satisfying the current query. """

        url = self.get_result_page_url(page=1)

        print(f"Requesting URL: {url}")
        self.driver.get(url)
        results_page = self.driver.page_source

        num_pages = self.get_num_pages(results_page)
        print(f"There are {num_pages} pages of results")

        results = self.extract_result_urls(results_page)
        print(f"Extracted {len(results)} results from page 1")

        for page_num in range(2, num_pages + 1):
            url = self.get_result_page_url(page=page_num)
            
            print(f"Requesting URL: {url}")
            self.driver.get(url)
            results_page = self.driver.page_source

            new_results = self.extract_result_urls(results_page)
            print(f"Extracted {len(new_results)} results from page {page_num}")

            results = results + new_results
            sleep(uniform(2, 5))

        return results


    def get_num_pages(self, results_page: str):
        """ Returns the number of pages of results; this info is found in the first page of results. """

        results_per_page = 30
        results_el = 'html body div#wrapper div#main div.container div.listing-top h1#h1-container.listing-title'
        page = bs(results_page, 'html.parser')
        el = page.select_one(results_el)

        if el is None:
            print(f"Cannot find element from selector {results_el}")
            print(f"Saving webpage to error.html for inspection...")
            
            with open('error.html', 'w') as f:
                f.write(results_page)
                
            raise ValueError("Invalid selector when looking for number of results")

        try:
            num_results = int(el.text.strip().split(' ')[0])
        except ValueError:
            print(f"Cannot extract number of results from: {el.text.strip()}")
            pass
        
        return - (-num_results // results_per_page)


    def extract_result_urls(self, results_page: str):
        """ Get ads urls from a page of results. """

        page = bs(results_page, 'html.parser')
        results_els = 'html body div#wrapper div#main div.container main#main-content.listing-items section.items-container article.item.item-multimedia-container div.item-info-container a.item-link'
        els = page.select(results_els)

        if len(els) == 0:
            raise 'Cannot find any result in current page!'

        results = list()
        
        for el in els:
            results.append(el['href'])
            
        return results


    def run(self):
        """ Runs the scraper and saves the info into a csv file. """
        
        results = self.get_result_urls()
        csv_file = f"{self.query.neighbourhood}.csv"

        try:
            df = pd.read_csv(csv_file)
        except:
            df = pd.DataFrame(columns=['title', 'url', 'sqm', 'rooms', 'state', 'elevator', 'price'])

        for result in results:
            url = f"https://www.idealista.com{result}"
            
            if len(df[df.url == url]) > 0:
                print('House already present, skipping...')
                continue
            
            print(f"Requesting URL: {url}")
            self.driver.get(url)
            page = self.driver.page_source
            
            page = bs(page, 'html.parser')
            
            try:
                title = page.select_one('.main-info__title-main').text.strip()
            except:
                print('Warning: cannot extract title!')
                title = 'Unknown title'
                
            try:
                sqm = page.select_one('.info-features > span:nth-child(1) > span:nth-child(1)').text.strip()
                sqm = int(sqm)
            except:
                print('Warning: cannot extract sqm')
                sqm = 0
            
            try:
                rooms = page.select_one('.info-features > span:nth-child(2) > span:nth-child(1)').text.strip()
                rooms = int(rooms)
            except:
                print('Warning: cannot extract rooms')
                rooms = 0
                
            state = 'second_hand'
                
            try:
                info_pts = page.select('.details-property-feature-one > div:nth-child(2) > ul:nth-child(1) > li')
                
                for el in info_pts:
                    txt = el.text.strip()
                    if txt in list(self.house_state.keys()):
                        state = self.house_state[txt]
                        break
            except:
                print('Error when trying to check house state')
                
            elevator = False
            
            try:
                building_info_pts = page.select('.details-property-feature-two > div:nth-child(2) > ul:nth-child(1) > li')
                
                for el in building_info_pts:
                    txt = el.text.strip()
                    if 'con ascensor' in txt:
                        elevator = True
                        break
            except:
                print('Error when trying to check for elevator')
                
            try:
                price_txt = page.select_one('span.txt-bold:nth-child(1)').text.strip()
                price_num = ''.join(c for c in price_txt if c.isdigit())
                price = int(price_num)
            except:
                print('Warning: cannot extract price')
                price = 0
                
            print(f"Extracted data")
            print(f"\tTitle:    {title}")
            print(f"\tSqm:      {sqm}")
            print(f"\tRooms:    {rooms}")
            print(f"\tState:    {state}")
            print(f"\tElevator: {elevator}")
            print(f"\tPrice:    {price}")
            
            df.loc[len(df),:] = [title, url, sqm, rooms, state, elevator, price]
            df.to_csv(csv_file, index=False)
            
            sleep(uniform(2, 5))
            
        return df