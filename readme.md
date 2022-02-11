# Scraping Supermarkets Product

In this project I manage and developing python script to scrape products data from online supermarkets websites.

* [Ah](https://www.ah.nl/)
* [Spar](https://www.spar.nl/)
* [Migros](https://produits.migros.ch/)
* [Walmart](https://www.walmart.com/)
* [Jumbo](https://www.jumbo.com/producten/)
* [Carrefour](https://www.carrefour.es/)

The objective I looking for is:
* product barcode data i.e. EAN or GTIN
* product name
* product url
* product image url(s)
* product brand
* product category
* product ingredients
* product calory information (if availabale)
* product nutritions score (if availabale)

## Script Development
All the script in this project developed in jupyter notebook (*.ipynb) first using requests, beautifulsoup, json, regex, asyncio, and aiohttp modules. For more details, requests module used to make a server GET/POST request on the backend, while beautifulsoup from bs4 module used to converting the html into bs4 object to make it easy extracting the desired data from the html tags. REGEX and JSON module used to manupulate strings and write out the data as JSON files. The last but not least, asyncio and aiohttp are used to make a asynchronous scraping system where aiohttp for the requests task and asyncio for the asynchronous tasks.

## Requirement Installations
```python
pip install -r requirements.txt
```