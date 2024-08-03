
from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse
import os
import sys

@dataclass
class Business:
    """holds business data"""
    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None
    reviews_count: int = None
    reviews_average: float = None
    latitude: float = None
    longitude: float = None

@dataclass
class BusinessList:
    """holds list of Business objects, and save to both excel and csv"""
    business_list: list[Business] = field(default_factory=list)
    save_at: str = 'output'

    def dataframe(self):
        """transform business_list to pandas dataframe"""
        return pd.json_normalize((asdict(business) for business in self.business_list), sep="_")

    def save_to_excel(self, filename):
        """saves pandas dataframe to excel (xlsx) file"""
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        self.dataframe().to_excel(f"{self.save_at}/{filename}.xlsx", index=False)

    def save_to_csv(self, filename):
        """saves pandas dataframe to csv file"""
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        self.dataframe().to_csv(f"{self.save_at}/{filename}.csv", index=False)

def extract_coordinates_from_url(url: str) -> tuple[float,float]:
    """helper function to extract coordinates from url"""
    coordinates = url.split('/@')[-1].split('/')[0]
    return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])

def main():
    # input 
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", type=str)
    parser.add_argument("-t", "--total", type=int)
    args = parser.parse_args()
    
    if args.search:
        search_list = [args.search]
        
    if args.total:
        total = args.total
    else:
        total = 1_000_000

    if not args.search:
        search_list = []
        input_file_name = 'input.txt'
        input_file_path = os.path.join(os.getcwd(), input_file_name)
        if os.path.exists(input_file_path):
            with open(input_file_path, 'r') as file:
                search_list = file.readlines()
                
        if len(search_list) == 0:
            print('Error occurred: You must either pass the -s search argument, or add searches to input.txt')
            sys.exit()
        
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://www.google.com/maps", timeout=60000)
        page.wait_for_timeout(5000)
        
        for search_for_index, search_for in enumerate(search_list):
            search_for = search_for.strip()
            print(f"-----\n{search_for_index} - {search_for}")

            page.locator('//input[@id="searchboxinput"]').fill(search_for)
            page.wait_for_timeout(3000)

            page.keyboard.press("Enter")
            page.wait_for_timeout(5000)

            page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

            previously_counted = 0
            while True:
                page.mouse.wheel(0, 10000)
                page.wait_for_timeout(3000)

                listings_count = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count()
                if listings_count >= total:
                    listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()[:total]
                    listings = [listing.locator("xpath=..") for listing in listings]
                    print(f"Total Scraped: {len(listings)}")
                    break
                else:
                    if listings_count == previously_counted:
                        listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()
                        print(f"Arrived at all available\nTotal Scraped: {len(listings)}")
                        break
                    else:
                        previously_counted = listings_count
                        print(f"Currently Scraped: {listings_count}")

            business_list = BusinessList()

            for listing in listings:
                try:
                    listing.click()
                    page.wait_for_timeout(5000)

                    name_attribute = 'aria-label'
                    address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
                    website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
                    phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
                    review_count_xpath = '//button[@jsaction="pane.reviewChart.moreReviews"]//span'
                    reviews_average_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]'
                    
                    business = Business()
                   
                    if listing.get_attribute(name_attribute):
                        business.name = listing.get_attribute(name_attribute)
                    else:
                        business.name = ""
                    if page.locator(address_xpath).count() > 0:
                        business.address = page.locator(address_xpath).all()[0].inner_text()
                    else:
                        business.address = ""
                    if page.locator(website_xpath).count() > 0:
                        business.website = page.locator(website_xpath).all()[0].inner_text()
                    else:
                        business.website = ""
                    if page.locator(phone_number_xpath).count() > 0:
                        business.phone_number = page.locator(phone_number_xpath).all()[0].inner_text()
                    else:
                        business.phone_number = ""
                    if page.locator(review_count_xpath).count() > 0:
                        business.reviews_count = int(
                            page.locator(review_count_xpath).inner_text().split()[0].replace(',','').strip()
                        )
                    else:
                        business.reviews_count = None
                        
                    if page.locator(reviews_average_xpath).count() > 0:
                        business.reviews_average = float(
                            page.locator(reviews_average_xpath).get_attribute(name_attribute).split()[0].replace(',','.')
                        )
                    else:
                        business.reviews_average = None
                    
                    business.latitude, business.longitude = extract_coordinates_from_url(page.url)

                    business_list.business_list.append(business)
                except Exception as e:
                    print(f'Error occurred while processing listing: {e}')
            
            business_list.save_to_excel(f"google_maps_data_{search_for}".replace(' ', '_'))
            business_list.save_to_csv(f"google_maps_data_{search_for}".replace(' ', '_'))

        browser.close()

if __name__ == "__main__":
    main()

#### installed libraries and packages for running the script 
# virtualenv venv
# venv/Scripts/activate
# pip install playwright pandas openpyxl
# playwright install chromium
# pip install -r requirements.txt
# pip freeze > requiremnt.txt

### for output write in terminal as:
python main.py -s "dentist Boston" -t 10