import requests
from pprint import pprint
from bs4 import BeautifulSoup
import json, re, os

headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"}

def render_html(url):
    req = requests.get(url,headers=headers)
    page = BeautifulSoup(req.text,"html.parser")
    return page

# find product name, brand, and its EAN code
def find_ean(page):
    for script in page.find_all("script",{"type":"text/javascript","charset":"utf-8"}):
        strt = r"var dataLayer \= window\.dataLayer \|\| \[\]\;dataLayer\.push\("
        end = r"\)\;"
        text = re.search(f"(?<={strt})(.*?)(?={end})",script.get_text())
        if text != None:
            text = json.loads(text.group())
            product = {
                "code": text['productEAN'],
                "brand": text['productBrand'],
            }
            return product

# find image url
def find_image_url(page):
    script = page.find("script",{"type":"application/ld+json"})
    script = json.loads(script.get_text())
    return script['name']

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
    if "nutriscore" in html.lower():
        it_has_nutriscore = True
    else:
        it_has_nutriscore = False

    # find EAN
    try: data = find_ean(page)
    except: data = {"code":None,"brand":None}
    if data == None: data = {"code":None,"brand":None}

    # find image urls
    try:
        script = page.find("script",{"type":"application/ld+json"})
        script = json.loads(script.get_text())
        image_url = script['image']
        product_name = script['name']
    except: product_name = image_url = None

    # find product container including ingredients, calories, and nutriscore value
    try: info_container = page.find("div",class_="nutrition")
    except: info_container = None
    
    if info_container != None:
        
        # find ingredients
        try: ingredients = info_container.find("p",class_="nutrition-ingredients__content").get_text().strip()
        except: ingredients = None
        
        # find calories
        try:
            cal = info_container.find("p",class_="nutrition-graph__kcal").get_text().strip().lower()
            netto = info_container.find("p",class_="nutrition-graph__info-text").get_text().strip().lower()
            netto = re.search("\d+ [a-z\/]+",netto)
            calories = None
            if netto != None:
                calories = f"{cal} / {netto.group()}"
        except: calories = None
            
        # find nutriscore
        try: nutriscore = info_container.find("div",class_="nutrition__score").get_text().strip()
        except: nutriscore = None

    else:
        ingredients = calories = nutriscore = None

    # find categories
    try:
        categories = []
        for li in page.find("ul",class_="breadcrumb__list").find_all("li"):
            categories.append(li.get_text().strip())        
        if len(categories) == 0:
            categories = None
    except: categories = None

    # product default data
    product_data = {
        "code" : data['code'],
        "sources" : [src],
        "image_url" : image_url,
        "small_image_url" : image_url,
        "product_name" : product_name,
        "brand" : data['brand'],
        "nutriscore" : nutriscore,
        "categories" : categories,
        "ingredients_text" : ingredients,
        "calories" : calories,
        "it_has_nutriscore": it_has_nutriscore
    }

    return filter_output(product_data,null_trsh=9)

if __name__ == "__main__":

    url = "https://www.carrefour.es/supermercado/berlinas-bombon-donuts-4-ud/R-715505824/p"
    req = requests.get(url,headers=headers)
    data = scraper(url, req.text)
    pprint(data,sort_dicts=False)