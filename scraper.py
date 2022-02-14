# import libraries
from click import option
import asyncfunctions as af
import os, sys, json, time
import numpy as np
import requests
import asyncio
import random

# import selenium libraries
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
import chromedriver_binary

# import logic libraries
from JumboHL import logic
from printer import print_green, print_red, print_yellow

# open the browser
options = Options()
options.add_argument("--headless")
options.add_argument("--level-log=3")
browser = Chrome(options=options)

def async_render(index,urls,dest_folder):
    '''
    Asynchronously make a request to the server in indexes sequence.
    :param index: list -> list of product index number
    :param urls: list -> list of product urls
    :param dest_folder: str -> destination folder for saving the json file
    :return results: list -> list of product data
    '''
    results = asyncio.run(af.render_all(logic.scraper,urls))
    for i,result in zip(index,results):
        dest_file = dest_folder + f"{i:05d}.json"
        if result != None:
            if not os.path.exists(dest_file):
                json.dump(result,open(dest_file,"w"),indent=4)

def manual_render(index,urls,dest_folder):
    '''
    Synchronously make a request to the server in indexes sequence.
    :param index: list -> list of product index number
    :param urls: list -> list of product urls
    :param dest_folder: str -> destination folder for saving the json file
    :return results: list -> list of product data
    '''
    for i,url in zip(index,urls):
        dest_file = dest_folder + f"{i:05d}.json"
        req = requests.get(url,headers=logic.headers)
        result = logic.scraper(url,req.text)
        if result != None:
            if not os.path.exists(dest_file):
                result['sources'] = [url]
                json.dump(result,open(dest_file,"w"),indent=4)
                print(i,end=",")
    print("\b. done.")

def rotating_proxy(index,urls,dest_folder):
    for i,url in zip(index,urls):
        dest_file = dest_folder + f"{i:05d}.json"
        all_proxies = json.load(open("proxies.json"))
        if len(all_proxies) > 0:
            while True:
                try:
                    proxy = random.choice(all_proxies)
                    proxies = {
                        "http": proxy,
                        "https": proxy
                    }
                    req = requests.get(url,headers=logic.headers,proxies=proxies)
                    result = logic.scraper(url,req.text)
                    if result != None:
                        if not os.path.exists(dest_file):
                            result['sources'] = [url]
                            json.dump(result,open(dest_file,"w"),indent=4)
                            print_green(f"{i} {all_proxies[0]}")
                            break
                except:
                    print_red(proxy)
                    all_proxies.remove(proxy)
                    json.dump(all_proxies,open("proxies.json","w"),indent=4)
        else:
            print_yellow("proxy list is empty")
            break

def selenium_webdriver(browser,index,urls,dest_folder):
    for i,url in zip(index,urls):
        dest_file = dest_folder + f"{i:05d}.json"
        browser.get(url)
        result = logic.scraper(url,browser.page_source)
        if result != None:
            if not os.path.exists(dest_file):
                result['sources'] = [url]
                json.dump(result,open(dest_file,"w"),indent=4)
                print(i,end=",")
    print("\b. done.")

# get the start point
try: st = int(sys.argv[1])
except: st = 0

# clear the terminal
os.system("cls")
beginning = time.time()
speed = [] # timespeed variable

# prepare the destionation folder
project_name = "JumboHL"
dest_folder = f"./{project_name}/raw_data/"

# read all the product urls
urls = json.load(open(f"./{project_name}/urls/product_urls.json"))
urls = list(dict.fromkeys(urls))

# iterate the scraping process in batches
index = list(range(0,len(urls)))

# filter the scraped urls
root = f"./{project_name}/raw_data/"
for file in os.listdir(root):
    if file.endswith("json"):
        i = int(file.replace(".json",""))
        data = json.load(open(root+file))
        if data != None:
            try:
                url = data['sources'][0]
                urls.remove(url)
                index.remove(i)
            except: os.remove(root+file)
        elif data == None:
            os.remove(root+file)

x, R = af.batchers(urls,80)
print(f"{len(urls)} data will be devided into {R} batch")
for r in range(st,R):
    print(f">> batch{r:03d}", end=" ")
    # print(f">> batch{r:03d}") # rotating proxy version
    try:
        start = time.time()
        a, b = x[r], x[r+1]

        # render all the urls asynchronously
        # results = async_render(index[a:b],urls[a:b],dest_folder)

        # render all the urls synchronously
        # results = manual_render(index[a:b],urls[a:b],dest_folder)

        # render all the urls synchronously using rotating proxy
        # rotating_proxy(index[a:b],urls[a:b],dest_folder)

        # render all the urls synchronously using rotating proxy
        selenium_webdriver(browser,index[a:b],urls[a:b],dest_folder)

        # printout the timestamp
        end = time.time()
        speed.append(end-start)
        est = af.sec2hms(int(np.mean(speed)*(R-r)))
        print_green(f"{end-start:.2f} sec (est. {est} left)")
    except:
        print_red("failed")
        break

# end statement
end = time.time()
time_str = f"{af.sec2hms(end-beginning)}"
print_yellow("done in " + time_str)