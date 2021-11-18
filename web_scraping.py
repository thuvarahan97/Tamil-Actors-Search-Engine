import codecs
import json

import requests
from bs4 import BeautifulSoup, Tag

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
    # Define actor dictionary
    actor = {}
    actor['name'] = ""
    actor['date_of_birth'] = ""
    actor['date_of_death'] = ""
    actor['place_of_birth'] = ""
    actor['spouse'] = []
    actor['children'] = []
    actor['movies'] = []
    actor['other_occupations'] = []
    actor['awards'] = []
    actor['intro'] = ""

    req = requests.get(url)
    page = req.content
    soup = BeautifulSoup(page, 'html.parser', from_encoding='utf-8')

    # Get actor name
    first_heading = soup.find('h1', attrs={'class': 'firstHeading'})
    actor['name'] = first_heading.get_text().strip()

    # Grab data from summarized info table
    info = soup.find('table', attrs={'class': 'infobox vcard'})
    try:
        info_body = info.find('tbody')

        bday = info_body.findChild('span', attrs={'class': 'bday'}, recursive=True)
        actor['date_of_birth'] = (bday.get_text().strip() if bday is not None else "")

        birthplace = info_body.findChild('span', attrs={'class': 'birthplace'}, recursive=True)
        actor['place_of_birth'] = (birthplace.get_text().strip() if birthplace is not None else "")

        dday = info_body.findChild('span', attrs={'class': 'dday'}, recursive=True)
        actor['date_of_death'] = (dday.get_text().strip() if dday is not None else "")

        info_rows = info_body.find_all('tr')[1:]
        for row in info_rows:
            row_th = row.find('th')
            if row_th is not None:
                row_td: Tag = row.find('td')
                row_key = row_th.get_text().replace(" ", " ").strip()
                if row_key == "பிறப்பு" and actor['place_of_birth'] == "":
                    row_value = []
                    for tag in row_td.find('span', attrs={'style': 'display:none'}).find_next_siblings():
                        if tag.name == 'a':
                            text = tag.get_text().strip()
                            if text not in row_value or text:
                                row_value.append(text)
                        elif tag.name == 'br' and len(row_value) > 0:
                            break
                    actor['place_of_birth'] = ", ".join(row_value)
                elif row_key == "வாழ்க்கைத் துணை" or row_key == "வாழ்க்கை துணைவர்(கள்)" or row_key == "வாழ்க்கை துணைவர்" or row_key == "துணைவர்":
                    row_value = get_info_row_texts(row_td)
                    actor['spouse'].extend(row_value)
                elif row_key == "பிள்ளை" or row_key == "பிள்ளைகள்":
                    row_value = get_info_row_texts(row_td)
                    actor['children'].extend(row_value)
                elif row_key == "பணி" or row_key == "பணிகள்":
                    row_value = get_info_row_texts(row_td)
                    actor['other_occupations'].extend(row_value)
                elif row_key == "விருது" or row_key == "விருதுகள்":
                    row_value = get_info_row_texts(row_td)
                    actor['awards'].extend(row_value)
    except Exception:
        print("No data")

    # Grab data from intro paragraphs
    intro_texts = []
    for tag in soup.find('div', attrs={'class': 'mw-parser-output'}).findChildren(recursive=False):
        if tag.name == 'p':
            for element in tag.find_all('sup', recursive=True):
                element.clear()
            intro_texts.append(tag.get_text().strip())
        elif tag.name != 'p' and tag.name != 'table':
            break
    actor['intro'] = " ".join(intro_texts)

    return actor


def get_single_text(text):
    return (text.strip().split("(")[0]).strip()


def get_info_row_texts(row_td: Tag):
    for br in row_td.find_all('br', recursive=True):
        br.insert(0, ',')
    for li in row_td.find_all('li', recursive=True):
        li.insert(0, ',')
    return map(get_single_text, filter(None, row_td.get_text().replace(" ", " ").replace("\n", ",").strip().split(",")))


if __name__ == "__main__":
    # # Scrape urls of a list of actors from web page
    # data = scrape_actors_links()
    #
    # # Save urls of actors in a csv file
    # df = pd.DataFrame.from_records(data)
    # df.to_csv('data_actors_links.csv', index=False, encoding='utf-8-sig')

    # Scrape single actor data
    data = scrape_actor_data(
        "https://ta.wikipedia.org/wiki/%E0%AE%95%E0%AE%AE%E0%AE%B2%E0%AF%8D%E0%AE%B9%E0%AE%BE%E0%AE%9A%E0%AE%A9%E0%AF%8D")

    # Save single actor data as json file
    with codecs.open('data_actor.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)
