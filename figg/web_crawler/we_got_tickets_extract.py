from bs4 import BeautifulSoup
import urllib
from datetime import datetime, date, timedelta

url = "http://www.wegottickets.com/searchresults/page/1/all"

f = urllib.urlopen(url)
html = f.read()
soup = BeautifulSoup(html)

def get_text(soup):
    # needs an exception for multiple 
    if len(soup) < 2:
        print "soup %s" % soup
    if not len(soup):
        return None
    else:
        return soup[0].text



listings_outer = soup.find_all("div", {'class': "ListingOuter"})
events = []

for listing in listings_outer:
    event = {}
    info = listing.find_all("div", {'class': "ListingAct"})
    assert(len(info) == 1)
    i = info[0]
    # get venue city
    unclean_cities = i.find_all("span", {'class': 'venuetown'})
    event["city"] = get_text(unclean_cities)
    event["venue"] = get_text(i.find_all("span", {'class': 'venuename'}))
    event["name"] = get_text(i.find_all("a", {'class': 'event_link'}))

    
    date_time_block = i.find_all("blockquote")

    if len(date_time_block) != 1:
        event["date"] = "unknown"
    else:
        date_time = date_time_block[0].text

        also_for_removal = i.find_all("span")
        for_removal = date_time_block[0].find_all("h3")[0].text
        date_time = date_time.replace(for_removal, "")

        for remove in also_for_removal:
            date_time = date_time.replace(remove.text, "")

        event["date"] = date_time.strip()



    div_price_info = listing.find_all("div", "searchResultsPrice")

    if(len(div_price_info) != 1):
        event["price"] = "unknown"
    else:
        price_info = div_price_info[0].find_all("strong")
        assert(len(price_info) == 1)
        event["price"] = price_info[0].text



    events.append(event)
