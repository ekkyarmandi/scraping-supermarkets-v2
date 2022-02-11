# import libraries
import asyncfunctions as af
import os, sys, json, time
import numpy as np
import requests
import asyncio

# import logic libraries
from SparHL import logic
from printer import print_green, print_red, print_yellow

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
    results = []
    for i,url in zip(index,urls):
        dest_file = dest_folder + f"{i:05d}.json"
        req = requests.get(url,headers=logic.headers)
        result = logic.scraper(url,req.content)
        if result != None:
            if not os.path.exists(dest_file):
                result['sources'] = [url]
                json.dump(result,open(dest_file,"w"),indent=4)
                print(i,end=",")
    print("\b. done.")
    return results

# get the start point
try: st = int(sys.argv[1])
except: st = 0

# clear the terminal
os.system("cls")
beginning = time.time()
speed = [] # timespeed variable

# prepare the destionation folder
project_name = "SparHL"
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
    try:
        start = time.time()
        a, b = x[r], x[r+1]

        # render all the urls asynchronously
        results = async_render(index[a:b],urls[a:b],dest_folder)

        # render all the urls synchronously
        # results = manual_render(index[a:b],urls[a:b],dest_folder)

        # printout the timestamp
        end = time.time()
        speed.append(end-start)
        est = af.sec2hms(int(np.mean(speed)*(R-r)))
        print_green(f"{end-start:.2f} sec (est. {est} left)")
    except:
        print_red("failed")

# end statement
end = time.time()
time_str = f"{af.sec2hms(end-beginning)}"
print_yellow("done in " + time_str)