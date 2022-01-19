import requests
from bs4 import BeautifulSoup as Soup


url = "https://jegornagel.com/stoic/"


def parser_page():
    articles_list = ''
    counter = 0
    html = requests.get(url)
    soup = Soup(html.text, 'html.parser')
    articles = soup.find(
        'ul', class_='wp-block-latest-posts__list is-style-default tw-heading-size-medium wp-block-latest-posts').find_all('a')
    for article in articles:
        counter += 1
        articles_list += "{}. [{}]({}) \n".format(counter, article.get_text(), article.get('href'))
    return articles_list
