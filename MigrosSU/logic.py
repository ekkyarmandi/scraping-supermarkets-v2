import requests
from pprint import pprint
from bs4 import BeautifulSoup
import json, re, os

headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"}

def render_html(url):
    req = requests.get(url,headers=headers)
    page = BeautifulSoup(req.text,"html.parser")
    return page

# find product details
def find_details(page):

    def find_table(text, split=False):
        table = {}
        for row in text.find("table").find_all("tr"):
            td = row.find_all("td")
            key = td[0].get_text().strip().lower().replace(" ","_")
            if split:
                table.update({
                    key: td[1].get_text().strip().split(", ")
                })
            else:
                table.update({
                    key: td[1].get_text().strip()
                })
        return table

    def find_calories(detail):
        table = detail.find("table")
        for th in table.find("thead").find_all("tr")[1].find_all("th"):
            try:
                d = re.findall("\d+",th.get_text())
                if len(d) > 0:
                    netto = th.get_text().strip()
                    break
            except: pass
        for tag in table.find_all("td"):
            if "kcal" in tag.text:
                cal = tag.get_text().strip()
                cal = re.search("\d+ kcal|\d+kcal",cal)
                if cal != None:
                    cal = cal.group()
                    break
        return f"{cal} / {netto}"

    content = {}
    for div in page.find("div",class_="product-stage").find_next_siblings("div"):
        try:
            title = div.find("h4").get_text().strip().lower().replace(" ","_")
            detail = div.find("div",{"id":re.compile("my-panel-*"),"role":"tabpanel"})
            if title == "numéros_d'article":
                detail = find_table(detail,split=True)
            elif title == "valeurs_nutritionnelles":
                detail = find_calories(detail)
            else:
                detail = find_table(detail)
            content.update({title:detail})
        except: pass
    
    return content

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

    # find product data
    scripts = page.find("script",{"type":"application/ld+json"})
    scripts = json.loads(scripts.text)
    for script in scripts:
        type_ = script['@type']
        if type_ == "WebPage":
            categories = []
            for cat in script['breadcrumb']['itemListElement'][2:-1]:
                categories.append(cat['item']['name'])
        else:
            try: name = script['name']
            except: name = None
            try: image = script['image']
            except: image = None
            try: brand = script['brand']['name']
            except: brand = None
            product = {
                "name": name,
                "image": image,
                "brand": brand
            }

    # find product details
    try: details = find_details(page)
    except: None
    if details != None:
        try: ingredients = details['ingrédients_et_allergènes']['ingrédients']
        except: ingredients = None
        try: calories = details['valeurs_nutritionnelles']
        except: calories = None
        try: code = details["numéros_d'article"]['gtin']
        except: code = None

    # product default data
    product_data = {
        "code" : code,
        "sources" : [src],
        "image_url" : product['image'],
        "small_image_url" : product['image'],
        "product_name" : product['name'],
        "brand" : product['brand'],
        "nutriscore" : None,
        "categories" : categories,
        "ingredients_text" : ingredients,
        "calories" : calories,
        "it_has_nutriscore": it_has_nutriscore
    }

    return filter_output(product_data,null_trsh=9)

if __name__ == "__main__":

    url = 'https://produits.migros.ch/poulet-crispy-14kg'
    req = requests.get(url,headers=headers)
    data = scraper(url, req.text)
    pprint(data,sort_dicts=False)