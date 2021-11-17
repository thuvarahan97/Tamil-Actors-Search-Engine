import pandas as pd
import requests
from bs4 import BeautifulSoup

base_url = 'https://ta.wikipedia.org'

page_indices = ['அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ',
                'க', 'ச', 'ட', 'த', 'ந', 'ப', 'ம', 'ய', 'ர', 'ல', 'வ', 'ஹ', 'ஸ', 'ஜ']


def scrape_actors_links():
    url = 'https://ta.wikipedia.org/w/index.php?title=%E0%AE%AA%E0%AE%95%E0%AF%81%E0%AE%AA%E0%AF%8D%E0%AE%AA%E0%AF%81:%E0%AE%A4%E0%AE%AE%E0%AE%BF%E0%AE%B4%E0%AF%8D%E0%AE%A4%E0%AF%8D_%E0%AE%A4%E0%AE%BF%E0%AE%B0%E0%AF%88%E0%AE%AA%E0%AF%8D%E0%AE%AA%E0%AE%9F_%E0%AE%A8%E0%AE%9F%E0%AE%BF%E0%AE%95%E0%AE%B0%E0%AF%8D%E0%AE%95%E0%AE%B3%E0%AF%8D&from='
    data = []
    actors_names = []
    count = 0
    print("Scraping URLs of Tamil actors from Wikipedia...")
    for i in page_indices:
        url_i = url + i
        req = requests.get(url_i)
        page = req.content
        soup = BeautifulSoup(page, 'html.parser', from_encoding='utf-8')
        page_category = soup.find('div', attrs={'class': 'mw-category'})
        page_category_group = page_category.find_all('div', attrs={'class': 'mw-category-group'})
        for group in page_category_group:
            rows = group.find('ul').find_all('li')
            for row in rows:
                actor = {}
                a = row.find('a')
                actor['name'] = a.get_text()
                actor['url'] = base_url + a.get('href')
                if actor['name'] not in actors_names:
                    data.append(actor)
                    actors_names.append(actor['name'])
                    count += 1
                    print('\rData Count: %s' % count, end='\r')
    print()
    return data


def scrape_actor_data(url):
    data = []
    req = requests.get(url)
    page = req.content
    soup = BeautifulSoup(page, 'html.parser', from_encoding='utf-8')
    info = soup.find('table', attrs={'class': 'infobox vcard'})
    try:
        info_body = info.find('tbody')
        info_rows = info_body.find_all('tr')[1:]
        for row in info_rows:
            row_th = row.find('th')
            if row_th is not None:
                row_td = row.find('td')
                row_key = row_th.get_text().replace(" ", " ").strip()
                row_value = row_td.get_text().replace(" ", " ").strip()
                val = {'th': row_key, 'td': row_value}
                data.append(val)
    except:
        print("No data")

    return data


if __name__ == "__main__":
    # Scrape urls of a list of actors from web page
    data = scrape_actors_links()

    # Save urls of actors in a csv file
    df = pd.DataFrame.from_records(data)
    df.to_csv('data_actors_links.csv', index=False, encoding='utf-8-sig')

    # # Scrape single actor data
    # data = scrape_actor_data("https://ta.wikipedia.org/wiki/%E0%AE%8E%E0%AE%B2%E0%AF%8D._%E0%AE%90._%E0%AE%9A%E0%AE%BF._%E0%AE%A8%E0%AE%B0%E0%AE%9A%E0%AE%BF%E0%AE%AE%E0%AF%8D%E0%AE%AE%E0%AE%A9%E0%AF%8D")
    # print(data)
    #
    # # Save single actor data as json file
    # with codecs.open('data_actor.json', 'w', encoding='utf-8') as file:
    #     json.dump(data, file, ensure_ascii=False)
   