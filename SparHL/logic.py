import requests
from pprint import pprint
from bs4 import BeautifulSoup
import json, re, os

headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"}

def render_html(url):
    req = requests.get(url,headers=headers)
    page = BeautifulSoup(req.text,"html.parser")
    return page

# find product calories
def find_calories(page):
    div = page.find("div",class_="c-offer__nutrition")
    netto = div.find("div",class_="title").get_text()
    netto = re.search("(?<=\()(.*?)(?=\))",netto).group()
    table = div.find("table")
    for tag in table.find_all("tr"):
        if "kcal" in tag.text:
            cal = int(tag.find_all("td")[-1].get_text())
    if cal != 0:
        calories = f"{netto} = {cal}"
        return calories
    else:
        return None

# filter the missing value
def filter_output(data,null_trsh):
    null = 0
    for key,value in data.items():
        if value == None or value == "":
            if value == "": data[key] = None
            null += 1
    if null == null_trsh:
        return None
    else:
        return data

def scraper(src,html):

    # convert text into dictionary
    page = BeautifulSoup(html,"html.parser")

    # find nutriscore word
    if "nutriscore" in html:
        it_has_nutriscore = True
    else:
        it_has_nutriscore = False

    # product default data
    product_data = {
        "code" : None,
        "sources" : [src],
        "image_url" : None,
        "small_image_url" : None,
        "product_name" : None,
        "brand" : None,
        "nutriscore" : None,
        "categories" : None,
        "ingredients_text" : None,
        "calories" : None,
        "it_has_nutriscore": it_has_nutriscore
    }

    # find product data
    for script in page.find_all("script",{"type":"application/ld+json"}):
        product = json.loads(script.get_text())
        type_ = product['@type']
        if type_ == "Product":
            product_data['code'] = product['gtin13']
            product_data['image_url'] = product['image']
            product_data['small_image_url'] = product['image']
            product_data['product_name'] = product['name']
            product_data['brand'] = product['brand']
        elif type_ == "BreadcrumbList":
            categories = []
            for item in product['itemListElement']:
                categories.append(item['item']['name'])
            product_data['categories'] = categories

    # find product calories
    try: calories = find_calories(page)
    except: calories = None

    # find product ingredients
    try: ingredients = page.find("div",class_="c-offer__ingredients-body").get_text().strip()
    except: ingredients = None

    # assign all the retrive data
    product_data['calories'] = calories
    product_data['ingredients_text'] = ingredients            
    return filter_output(product_data,null_trsh=9)

if __name__ == "__main__":

    url = 'https://www.spar.nl/smaakt-3305554/'
    req = requests.get(url,headers=headers)
    data = scraper(url, req.text)
    pprint(data,sort_dicts=False)