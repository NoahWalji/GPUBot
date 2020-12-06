import requests
import random
import difflib
import smtplib

from flask import Flask, render_template, request
from bs4 import BeautifulSoup


app = Flask(__name__)

## Global Variables
query = ""
finalResults = []
currentPage = []
pageNum = 0

## Main Search Function
## Function is run upon a users submission of the search bar
## Returns: First 20 Results (Cost Lowest to Highest) and updates global
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
        if (url == "https://www.amazon.ca/s?k="+query+"&rh=n%3A677273011&ref=nb_sb_noss" or url == "https://www.canadacomputers.com/search/results_details.php?language=en&keywords="+query):
            print(content)
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

## Switches the view to the next page
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

## Switches the view to the previous page
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
@app.route("/")
def home():
    return render_template('main.html')

## Runs if any forms are submitted (Next Page, Previous Page and Search Submit)
@app.route("/", methods=["GET","POST"])
def queryResults():
    global query;
    global currentPage;

    ## Figures out if the next button, previous button or serach button was pressed and gets the items
    if ('query' in request.form):
        query = request.form.get('query', 0)
        items = search(query);
    
    elif ('next' in request.form):
        items = nextPage()
    
    elif ('previous' in request.form):
        items = prevPage()
    
    if (len(items) > 0):
        return render_template('results.html', search = items, query = query);
    
    else:
        return render_template('results.html', search = currentPage, query = query);

@app.route("/contact")
def contact():
    return render_template('contact-form.html')


@app.route("/contact", methods=["POST"])
def contactSubmission():
    senderEmail = request.form.get("senderEmail")
    senderSubject = request.form.get("senderSubject")
    senderContents = request.form.get('senderContents')

    if (not senderEmail or not senderSubject or not senderContents):
        return render_template('contact-form.html', message= "Error: Please fill out all fields and try again")

    message = 'Subject: {}\n\n{}'.format("[GPUBot Client]: " + senderSubject, "Sender Email: " + senderEmail + "\n" + senderContents)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("gpubotsender@gmail.com", "cp317assignment")
    server.sendmail("gpubotsender@gmail.com", "gpubotreceiver@gmail.com", message)

    return render_template('contact-form.html', message= "Success: We have received your message! Please allow us 48 hours to respond.")

if __name__ == '__main__':
    app.run(debug=True,threaded=True)

    
