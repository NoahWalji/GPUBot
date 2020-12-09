import requests
import random
import difflib

from flask import Flask, render_template, request, Blueprint
from bs4 import BeautifulSoup

## Flask Blueprint
searchPage = Blueprint('searchPage', __name__, template_folder='templates', static_folder="static")

## Global Variables
query = ""
finalResults = []
currentPage = []
pageNum = 0

"""
Main Search Function
Function is run upon a users submission of the search bar. It takes the query, searchs all retailers sites and returns a list of results
Made By: Noah Walji
Arguments: Query (String: The search query submitted by the user)
Variables: 
    - currentPage: The users current page results
    - divs: Array (Array of divs to get results from each site)
    - items: Array of items found using div in the results
    - finalResults: Array of all results
    - headers: Dictonary of header to use when searching
    - pageNum: Page number currently on
    - productName, price, rating, store
    - query: String (Query user submitted)
    - url: Array (List of urls to search from)
    - user_agent_list: Array (List of user agents to use when searching)
Input: Query, Output: Final Results
Error Handling: If price is not found, or less than $300 remove from list, 

Returns: First 20 Results (Cost Lowest to Highest) and updates global
"""
def search(query):
    ## Replace spaces with url friendly
    query = query.replace(" ", "+")
    ## List of URLS and divs used on URLS
    urls = ["https://www.amazon.ca/s?k="+query+"&rh=n%3A677273011&ref=nb_sb_noss", "https://www.newegg.ca/p/pl?d="+query, "https://www.canadacomputers.com/search/results_details.php?language=en&keywords="+query]
    divs = ['a-section a-spacing-medium', 'item-container','row mx-0']

    user_agent_list = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    ]

    ## Init globals and other variables
    global finalResults
    global pageNum
    global currentPage
    pageNum = 0
    finalResults = []
    currentPage = []

    ## Header for web scrapping TODO: (Change not sure if needed?)
    headers = {"User-Agent":random.choice(user_agent_list), 
    "Accept-Encoding":"gzip, deflate", 
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
    "DNT":"1",
    "Connection":"close", 
    "Upgrade-Insecure-Requests":"1"}

    ## Main For Loop: Loops through all URLS and scrapes each URL with the selected item
    i = 0;
    for url in urls:

        ## Init the scrape for the given url
        results = requests.get(url, headers=headers)
        content = results.content
        soup = BeautifulSoup(content, "lxml")
        ## Find all the divs with the selected div for the URL
        items = soup.findAll('div', divs[i])
        

        ## Loop through all the divs found and get item details (name, price, rating, url)
        for item in items:
            ## Run if it is an Amazon link
            if (i == 0):
                itemName = item.find('span','a-size-medium a-color-base a-text-normal').text if item.find('span','a-size-medium a-color-base a-text-normal') else ""
                itemName = itemName[0:70] + "..."
                itemPrice = float(item.find('span','a-offscreen').text.replace("CDN$", "").replace(",","")) if item.find('span','a-offscreen') else 0
                itemRating = item.find('span','a-icon-alt').text if item.find('span','a-icon-alt') else "No Ratings"
                itemURL = "http://amazon.ca/" + item.find('a', 'a-link-normal a-text-normal')['href']
                result = [itemName,itemPrice,itemRating,"Amazon",itemURL]
            
            ## Run if its a NewEgg link
            elif (i == 1):
                itemName = item.find('a','item-title').text if item.find('a','item-title') else ""
                itemName = itemName[0:70] + "..."
                itemPrice = float(item.find('li','price-current').text.replace("$","").replace(",","").replace(u'\u2013',"").split("(")[0]) if item.find('li','price-current').text else 0
                itemRating = item.find('a','item-rating')['title'] if item.find('a','item-rating') else "No Ratings"
                itemRating = itemRating.replace("+", " ")
                itemRating = itemRating + " out of 5 stars"
                itemURL = item.find('a', 'item-img')['href']
                result = [itemName,itemPrice,itemRating,"NewEgg",itemURL]
            
            ## Run if its a Canada Computers link
            elif (i == 2):
                itemName = item.find('span','productTemplate_title').text if item.find('span','productTemplate_title') else ""
                itemName = itemName[0:70] + "..."
                itemPrice = float(item.find('span','pq-hdr-product_price').text.replace("$","").replace(",","")) if item.find('span','pq-hdr-product_price') else 0
                itemRating = "No Ratings Available"
                itemURL = item.find('a')['href']
                result = [itemName,itemPrice,itemRating,"Canada Computers", itemURL]
            
            ## If Price is zero it means that the item is either sold out, or has multiple prices: not included
            if (itemPrice > 299):
                finalResults.append(result)
        i = i + 1
    
    ## Sort based on price (Lowest to highest)
    finalResults = sorted(finalResults, key=lambda x: difflib.SequenceMatcher(None, x[0], query).ratio(), reverse=True)
    ## Set current page (first page) and return 
    currentPage = finalResults[:20]
    return currentPage

"""
Next Page  Function
Function produces the next page of results
Made By: Noah Walji
Variables: 
    - currentPage: The users current page results
    - finalResults: Array of all results
    - pageNum: Page number currently on

Error Handling: If there are none left return nothing

Returns: Updated current page
"""
def nextPage():
    global finalResults
    global pageNum
    global currentPage
    

    ## If there are items left, add the page number and get the next 20 results in the list
    if (len(finalResults) != 0):
        if (len(finalResults[20*(pageNum+1):20*(pageNum+2)]) > 0):
            pageNum = pageNum + 1;
            currentPage = finalResults[20*pageNum:20*(pageNum+1)]
    return currentPage

"""
Previous Page  Function
Function produces the previous page of results
Made By: Noah Walji
Variables: 
    - currentPage: The users current page results
    - finalResults: Array of all results
    - pageNum: Page number currently on

Error Handling: If there are none left or on first page return nothing

Returns: Updated current page
"""
def prevPage():
    global finalResults
    global pageNum
    global currentPage
    

    ## If there are items left, sub the page number and get the previous 20 results in the list
    if (len(finalResults) > 0 and pageNum != 0):
        pageNum = pageNum - 1;
        if (len(finalResults[20*(pageNum):20*(pageNum+1)]) > 0):
            currentPage = finalResults[20*(pageNum):20*(pageNum+1)]
    return currentPage

## Route for the homepage 
@searchPage.route("/")
def home():
    return render_template('main.html')   

## Runs if any forms are submitted (Next Page, Previous Page and Search Submit)
@searchPage.route("/", methods=["GET","POST"])
def queryResults():
    global query;
    global currentPage;
    global pageNum;

    ## Figures out if the next button, previous button or serach button was pressed and gets the items
    if ('query' in request.form):
        query = request.form.get('query', 0)
        items = search(query);
    
    elif ('next' in request.form):
        items = nextPage()
    
    elif ('previous' in request.form):
        items = prevPage()
    
    if (len(items) > 0):
        return render_template('results.html', search = items, query = query, pageNum = pageNum);
    
    else:
        return render_template('results.html', search = currentPage, query = query, pageNum = pageNum);