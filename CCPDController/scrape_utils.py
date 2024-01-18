# '''
# Scrape stock images URL from Amazon, HomeDepot etc.
# Original Author: ouyangxue-0407
# '''
# import time
# import random
# import requests
# from PIL import Image
# from io import BytesIO
from fake_useragent import UserAgent
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options

# # random wait time between scrape
# random_wait = lambda : time.sleep(random.randint(30, 50))

# # # Amazon US
# # def search_amazon(self: str):
# #     url = f"https://www.amazon.com/s?k={self.query}"
# #     page = self.context.new_page()
# #     page.goto(url)
# #     page.wait_for_load_state('domcontentloaded')
# #     first_product_link = page.query_selector("a.a-link-normal")
# #     if first_product_link:
# #         first_product_img = first_product_link.query_selector("img")
# #         if first_product_img:
# #             img_src = first_product_img.get_attribute('src')
# #             return img_src
# #     return None

# # # Amazon CA
# # def search_amazon_ca(query: str):
# #     play = sync_playwright().start()
# #     browser = play.chromium.launch(
# #         headless=True,
# #         channel="msedge",
# #         args=[
# #             '--enable-automation',
# #             '--window-size=1280,768',
# #         ],
# #     )
# #     context = browser.new_context()
# #     url = f"https://www.amazon.ca/s?k={query}"
# #     page = context.new_page()
# #     page.goto(url)
# #     page.wait_for_load_state('domcontentloaded')
    
# #     # start scraping
# #     first_product_link = page.query_selector("a.a-link-normal")
# #     if not first_product_link:
# #         return None
    
# #     first_product_img = first_product_link.query_selector("img")
# #     if not first_product_img:
# #         return None
    
# #     img_src = first_product_img.get_attribute('src')
# #     browser.close()
# #     return img_src

# # # HomeDepot US
# # def search_homedepot(query: str):
# #     url = f"https://www.homedepot.com/s/{query}"
# #     page = self.context.new_page()
# #     page.goto(url)
# #     page.wait_for_load_state('domcontentloaded')
# #     first_product_link = page.query_selector("a.product-image")
# #     if first_product_link:
# #         first_product_img = first_product_link.query_selector("img")
# #         if first_product_img:
# #             img_src = first_product_img.get_attribute('src')
# #             return img_src
# #     return None

# # # HomeDepot CA
# # def search_homedepot_ca(query: str):
# #     url = f"https://www.homedepot.ca/search?q={query}"
# #     page = self.context.new_page()
# #     page.goto(url)
# #     page.wait_for_load_state('domcontentloaded')
# #     first_product_link = page.query_selector("a.acl-product-card__image-link")
# #     if first_product_link:
# #         first_product_img = first_product_link.query_selector("img")
# #         if first_product_img:
# #             img_src = first_product_img.get_attribute('src')
# #             return img_src
# #     return None

# generate 10 Random user agent
def generate_ua():
    ua = UserAgent()
    user_agents = []
    for i in range(10):
        user_agent = ua.random
        user_agents.append(user_agent)
    return user_agents

# # user agent array
# uaArr = generate_ua()

# # selenium webdriver options
# options = webdriver.ChromeOptions()
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("--disable-extensions")
# options.add_argument("--profile-directory=Default")
# options.add_argument("--disable-plugins-discovery")
# options.add_argument("--lang=en")
# options.add_argument(f'user-agent={random.choice(uaArr)}')



# def create_driver(user_agent):
#     options = Options()
#     options = webdriver.ChromeOptions()
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--profile-directory=Default")
#     options.add_argument("--disable-plugins-discovery")
#     options.add_argument("--lang=en")
#     options.add_argument(f'user-agent={random.choice(user_agent)}')
#     options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
#     options.add_experimental_option('excludeSwitches', ['enable-logging'])
#     driver = webdriver.Chrome(options=options, executable_path='d:\\CCP-AUTOMATION\\chromedriver.exe')
#     return driver

# def scrape(url: str):
#     driver = webdriver.Chrome(options=options)
#     driver.get(url)
#     div_elements = driver.find_elements(By.CSS_SELECTOR, "div.mediagallery__mainimage")
#     if div_elements:
#         img_element = div_elements[0].find_element("tag name", "img")
#         img_url = img_element.get_attribute("src")
#         response = requests.get(img_url)
#         img_bytes = BytesIO(response.content)
#         img = Image.open(img_bytes)
#         img.save(os.path.join(target_folder, f"{item}.jpg"))
#         return driver
#     #except Except:
#     else:
#         div_elements = driver.find_elements(By.CSS_SELECTOR, "div.canvas-container")
#         if div_elements:
#             button=div_elements[0].find_element(By.CLASS_NAME, "modal-button")
#             button.click()
#             div_img_elements = div_elements[0].find_elements(By.XPATH, "//div[contains(@class, 'image-container') and contains(@class, 'ng-star-inserted')]")
#             img_element = div_img_elements[0].find_element("tag name", "img")
#             img_url = img_element.get_attribute("src")
#             try:
#                 with urllib.request.urlopen(url, timeout=5) as response:
#                     image_content = response.read()
#                     with open(os.path.join(target_folder, f"{item}.jpg"), "wb") as file:
#                         file.write(image_content)
#                 return driver
#             except:
#                 print("No Image Found Time Out")
#                 return driver
#         else:
#             print("No Image Found")
#             return driver
#     return None

