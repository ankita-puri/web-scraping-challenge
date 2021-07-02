from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager



def get_mars_news(browser):

    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # check if element present
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    html = browser.html
    news_soup_parser = soup(html, 'html.parser')

    try:
        news = news_soup_parser.select_one('div.list_text')
        news_title = news.find("div", class_="content_title").get_text()
        news_p = news.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def get_featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    full_image = browser.find_by_tag('button')[1]
    full_image.click()

    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        img_url = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    # Getting access denied on full S3 path
    img_url = f'https://spaceimages-mars.com/{img_url}'

    return img_url

def get_mars_facts():
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    df.columns = ['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    return df.to_html(classes="table table-striped")


def get_hemispheres(browser):
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser.visit(url)

    hemisphere_image_urls = []
    for i in range(4):
        browser.find_by_css("a.product-item img")[i].click()
        hemisphere = scrape_hemisphere(browser.html)
        hemisphere['img_url'] = hemisphere['img_url']
        hemisphere_image_urls.append(hemisphere)
        browser.back()

    return hemisphere_image_urls


def scrape_hemisphere(html_text):
    hemisphere_soup = soup(html_text, "html.parser")

    try:
        title = hemisphere_soup.find("h2", class_="title").get_text()
        sample = hemisphere_soup.find("a", text="Sample").get("href")

    except AttributeError:
        title = None
        sample = None

    hemispheres = {
        "title": title,
        "img_url": sample
    }

    return hemispheres

def scrape():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    news_title, news_p = get_mars_news(browser)
    featured_image = get_featured_image(browser)
    mars_facts = get_mars_facts()
    hemispheres = get_hemispheres(browser)



    data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image,
        "facts": mars_facts,
        "hemispheres": hemispheres,
        "last_modified": dt.datetime.now()
    }

    browser.quit()
    return data


if __name__ == "__main__":
    
    # If running as script, print scraped data
    print(scrape())
