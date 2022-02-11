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
    table = page.find("table",class_=re.compile("product-info-nutrition_table*"))
    netto = [net.text for net in table.find("thead").find_all("th")[1:]]
    cals = []
    for td in table.find_all("td"):
        if "kcal" in td.text:
            calory = re.search("\d+ kcal|\d+kcal",td.text).group()
            cals.append(calory)
    calories = []
    for net,cal in zip(netto,cals):
        net = net.lower().replace("per","").strip()
        cal = "/".join([cal,net])
        calories.append(cal)
    return ", ".join(calories)

# find product ingredients
def find_ingredients(page):
    for h2 in page.find_all("h2"):
        if h2.text.lower() == "ingrediënten":
            ingredients = h2.find_next().get_text()
            ingredients = re.sub("\s+"," ",ingredients)
            for w in re.findall("\.[A-Za-z]",ingredients):
                new_w = w.replace(".",". ")
                ingredients = ingredients.replace(w,new_w)
            try:
                a,b = re.search("ingrediënten",ingredients.lower()).span()
                ingredients = ingredients.replace(ingredients[a:b],"").replace(":","")
                ingredients = ingredients.strip()
            except: pass
            if ingredients[-1] != ".":
                ingredients += "."
    return ingredients

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
    }

    # find product data
    try:
        for script in page.find_all("script",{"type":"application/ld+json"}):
            product = json.loads(script.get_text())
            type_ = product['@type']
            if type_ == "Product":
                product_data['code'] = product['gtin13']
                product_data['small_image_url'] = product['image']
                product_data['product_name'] = product['name']
                product_data['brand'] = product['brand']['name']
            elif type_ == "BreadcrumbList":
                categories = []
                for item in product['itemListElement'][1:]:
                    categories.append(item['item']['name'])
                product_data['categories'] = categories
    except: pass

    # find product nutriscore
    try: nutriscore = page.find("div",class_=re.compile("nutriscore*")).find("title").get_text().split(" ")[-1]
    except: nutriscore = None

    # find product image url
    try: image_url = page.find("img",{"data-testhook":"product-image"})['src']
    except: image_url = None

    # find product calories
    try: calories = find_calories(page)
    except: calories = None

    # find product ingredients
    try: ingredients = find_ingredients(page)
    except: ingredients = None

    # assign the retrive data and filter missing values
    product_data['nutriscore'] = nutriscore
    product_data['image_url'] = image_url
    product_data['calories'] = calories
    product_data['ingredients_text'] = ingredients
    return filter_output(product_data,null_trsh=9)

if __name__ == "__main__":

    url = 'https://www.ah.nl/producten/product/wi515339/douwe-egberts-koffiecups-lungo-pakket'
    req = requests.get(url,headers=headers)
    data = scraper(url, req.text)
    pprint(data,sort_dicts=False)