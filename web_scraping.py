import json
import csv
import pandas as pd
import requests
from bs4 import BeautifulSoup
import codecs
import tamil.utf8 as utf8

page_indices = ['அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ',
      'க', 'ச', 'ட', 'த', 'ந', 'ப', 'ம', 'ய', 'ர', 'ல', 'வ', 'ஹ', 'ஸ', 'ஜ']


def scrape():
    url = 'https://ta.wikipedia.org/w/index.php?title=%E0%AE%AA%E0%AE%95%E0%AF%81%E0%AE%AA%E0%AF%8D%E0%AE%AA%E0%AF%81:%E0%AE%A4%E0%AE%AE%E0%AE%BF%E0%AE%B4%E0%AF%8D%E0%AE%A4%E0%AF%8D_%E0%AE%A4%E0%AE%BF%E0%AE%B0%E0%AF%88%E0%AE%AA%E0%AF%8D%E0%AE%AA%E0%AE%9F_%E0%AE%A8%E0%AE%9F%E0%AE%BF%E0%AE%95%E0%AE%B0%E0%AF%8D%E0%AE%95%E0%AE%B3%E0%AF%8D&from='
    data = []
    actors_names = []
    count = 0
    for i in page_indices:
        url_i = url + i
        req = requests.get(url_i)
        print(req.headers['Content-Type'])

        page = req.content
        soup = BeautifulSoup(page.decode('utf-8'), 'lxml', from_encoding='utf-8')
        page_category = soup.find('div', attrs={'class': 'mw-category'})
        page_category_group = page_category.find_all('div', attrs={'class': 'mw-category-group'})
        for group in page_category_group:
            rows = group.find('ul').find_all('li')
            for row in rows:
                actor = {}
                a = row.find('a')
                actor['name'] = a.get_text()
                actor['url'] = 'https://ta.wikipedia.org' + a.get('href')
                if actor['name'] not in actors_names:
                    data.append(actor)
                    actors_names.append(actor['name'])
                count += 1
                # letters = utf8.get_letters(actor['name'])
                # print(actor['name'])

                print('\rScrapped Data Count: %s' % count, end='\r')

    print()
    print("Total Data:", len(data))
    print(count)
    return data




if __name__ == "__main__":
    data = scrape()

    df = pd.DataFrame.from_records(data)
    df.to_csv('data_actors_links.csv', index=False, encoding='utf-8-sig')

    # with codecs.open('data.json', 'w', encoding='utf-8') as file:
    #     # csv_writer = csv.writer(csv_file)
    #     json.dump(data, file, ensure_ascii=False)

    # csv_file = open('data_file.csv', 'w')
    # csv_writer = csv.writer(csv_file)
    # count = 0
    # for data in jsondata:
    #     if count == 0:
    #         header = data.keys()
    #         csv_writer.writerow(header)
    #         count += 1
    #     csv_writer.writerow(data.values())
    #
    # csv_file.close()
