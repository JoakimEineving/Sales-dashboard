from flask import Flask, render_template
import apikey as apikey
import requests
import json
import datetime as datetime
from collections import Counter





# Feel free to import additional libraries if you like

app = Flask(__name__, static_url_path='/static')

# Paste the API-key you have received as the value for "x-api-key"


#get current date minus one year
def one_year():
    today = datetime.date.today()
    year = datetime.timedelta(days=365)
    return today - year

def one_month():
    today = datetime.date.today()
    month = datetime.timedelta(days=30)
    return today - month

print(one_year())
headers = {
        "Content-Type": "application/json",
        "Accept": "application/hal+json",
        "x-api-key": apikey.apikey
}


# Example of function for REST API call to get data from Lime
def get_api_data(headers, url):
    # First call to get first data page from the API
    response = requests.get(url=url,
                            headers=headers,
                            data=None,
                            verify=False)

    # Convert response string into json data and get embedded limeobjects
    json_data = json.loads(response.text)
    limeobjects = json_data.get("_embedded").get("limeobjects")

    # Check for more data pages and get thoose too
    nextpage = json_data.get("_links").get("next")
    while nextpage is not None:
        url = nextpage["href"]
        response = requests.get(url=url,
                                headers=headers,
                                data=None,
                                verify=False)

        json_data = json.loads(response.text)
        limeobjects += json_data.get("_embedded").get("limeobjects")
        nextpage = json_data.get("_links").get("next")

    return limeobjects
# Index page
@app.route('/')
def dashboard():
    
    # Example of API call to get deals
    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limeobject/deal/"
    params = f"?_limit=50&dealstatus=agreement&min-closeddate={one_year()}"
    url = base_url + params
    #count deals

    response_deals = get_api_data(headers, url)
    #count deals
    print(len(response_deals))
    print(one_year())
    
    #count deals per month
    
 

    #count average deal value and deals per month
    deal_value = 0
    deals_month = []
    for deal in response_deals:
        deal_value += deal.get("value")
        deals_month.append(deal.get("closeddate")[5:7])
    deals_month = Counter(deals_month)

    #convert to json
    deals_month = json.dumps(deals_month)
    
    print(deals_month)


    if len(response_deals) > 0:
        deal_value = int(deal_value / len(response_deals))
        return render_template('dashboard.html', deal_value=deal_value, deals_month=deals_month)
    else:
        deal_value = 0
        return render_template('dashboard.html', deal_value=deal_value, deals_month=deals_month)


# Example page
@app.route('/example')
def example():

    # Example of API call to get deals
    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limeobject/deal/"
    params = f"?_limit=50&dealstatus=agreement&min-closeddate={one_year()}"
    url = base_url + params
    #count deals

    response_deals = get_api_data(headers, url)
    #count deals
    print(len(response_deals))
    print(one_year())
    
    #count average deal value
    deal_value = 0
    for deal in response_deals:
        deal_value += deal.get("value")

    if len(response_deals) > 0:
        deal_value = deal_value / len(response_deals)
        return render_template('example.html', deals=response_deals, deal_value=deal_value)
    else:
        msg = 'No deals found'
        return render_template('example.html', msg=msg)


# You can add more pages to your app, like this:
@app.route('/myroute')
def myroute():
    mydata = [{'name': 'apple'}, {'name': 'mango'}, {'name': 'banana'}]

    return render_template('mytemplate.html', items=mydata)


# DEBUGGING
"""
If you want to debug your app, one of the ways you can do that is to use:
import pdb; pdb.set_trace()
Add that line of code anywhere, and it will act as a breakpoint and halt
your application
"""

if __name__ == '__main__':
    app.secret_key = 'somethingsecret'
    app.run(debug=True)