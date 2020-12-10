from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/scrape"
mongo = PyMongo(app)

    # conn = "mongodb://localhost:27017"
    # client = pymongo.MongoClient(conn)
    # db = client.scrape
    # collection = db.scraped_data

def scrape():

    #!/usr/bin/env python
    # coding: utf-8

    # ## NASA Mars News

    # Import Splinter, BeautifulSoup, and Pandas
    from splinter import Browser
    from bs4 import BeautifulSoup as bs
    import pandas as pd
    from webdriver_manager.chrome import ChromeDriverManager
    import requests
    from time import sleep


    executable_path = {"executable_path": ChromeDriverManager().install()}
    browser = Browser("chrome", **executable_path, headless=False)


    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=2)


    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = bs(html, 'html.parser')
    browser.quit()

    articles = news_soup.select('ul.item_list li.slide')

    news_title=articles[0].find("div", class_='content_title').get_text()
    news_p=articles[0].find("div", class_='article_teaser_body').get_text()


    # ## JPL Mars Space Images - Featured Image

    executable_path = {"executable_path": ChromeDriverManager().install()}
    browser = Browser("chrome", **executable_path, headless=False)

    browser.visit("https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars")
    html = browser.html
    browser.quit()


    soup = bs(html, 'html.parser')

    featured_image = soup.find('a', class_='fancybox')

    featured_image_url=featured_image["data-fancybox-href"]
    home_site='https://www.jpl.nasa.gov'
    featured_image_url=home_site+featured_image_url


    # ## Mars Weather

    executable_path = {"executable_path": ChromeDriverManager().install()}
    browser = Browser("chrome", **executable_path, headless=False)

    browser.visit("https://twitter.com/marswxreport?lang=en")
    sleep(4)

    # Optional delay for loading the page
    
    browser.is_element_present_by_css("span.css-901oao", wait_time=2)

    html = browser.html
    soup = bs(html, 'html.parser')
    browser.quit()

    weather_soup = soup.find_all('div', class_='css-1dbjc4n r-j7yic r-qklmqi r-1adg3ll r-1ny4l3l')
    mars_weather=[]

    for x in range(len(weather_soup)):
        tweet=weather_soup[x].find_all("span", class_='css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0')
        for i in range(len(tweet)):
            if 'InSight' in tweet[i].get_text():
                weather_tweet = tweet[i].get_text()
                mars_weather.append(weather_tweet)
                break
                
    mars_weather=mars_weather[0]


    # ## Mars Facts

    url = 'https://space-facts.com/mars/'

    tables = pd.read_html(url)


    mars_facts_df = tables[1]
    mars_facts_df=mars_facts_df.set_index("Mars - Earth Comparison")


    mars_facts_htmldf= mars_facts_df.to_html().replace('\n','')


    # ## Mars Hemispheres

    img_url = []
    title = []
    hemisphere_image_urls = []

    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    html = requests.get(url).text
    soup = bs(html, 'html.parser')

    results_main_page=soup.find_all("div", class_="item")

    for x in range(len(results_main_page)):
        image_title = results_main_page[x].a.h3
        image_title = image_title.get_text()
        title.append(image_title)

        link = results_main_page[x].a["href"]
        main_site = "https://astrogeology.usgs.gov"
        image_link = main_site + link
        url = image_link
        
        html = requests.get(url).text
        soup = bs(html, 'html.parser')
        
        results=soup.select("ul>li")
        
        for x in range(len(results)):
            if "original" in (results[x].get_text()).lower():
                each_img_url = results[x].a["href"]
                img_url.append(each_img_url)
                
                img_urls_dic={
                    "title":image_title,
                    "img_url":each_img_url
                }
                
                hemisphere_image_urls.append(img_urls_dic)
                
                break

        scraped_data={
            "news_title": news_title,
            "news_story" : news_p,
            "featured_image_url" : featured_image_url,
            "mars_weather" : mars_weather,
            "mars_facts_df" : mars_facts_htmldf,
            "hemisphere_image_urls" : hemisphere_image_urls
        }

    return  scraped_data

#ROUTES
@app.route("/")
def mars_data():

    # scraped_info = collection.find_one()

    scraped_data = mongo.db.scraped_data.find_one()

    return render_template("index.html", scraped_data=scraped_data)

@app.route("/scrape")
def scrape_fn():  

    #WE CREATE THE COLLECTIONS AND ADD THEM TO THE DATABASE THAT I CREATED IN THE CELLS ABOVE

    scraped_data = mongo.db.scraped_data
    scraped_function = scrape()
    scraped_data.update({}, scraped_function, upsert=True)

    # conn = "mongodb://localhost:27017"
    # client = pymongo.MongoClient(conn)
    # db = client.scrape
    # collection = db.scraped_data

    # collection.insert_one(scraped_function)

    
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)