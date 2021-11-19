import codecs
import json
import re
from typing import List

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
    actor['name'] = first_heading.get_text().strip().split("(")[0].strip()

    # Grab data from summarized info table
    info = soup.find('table', attrs={'class': 'infobox'})
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
                    removable_values = ["நடிகர்", "திரைப்பட நடிகர்"]
                    for val in removable_values:
                        if val in row_value:
                            row_value.remove(val)
                    actor['other_occupations'].extend(row_value)
                elif row_key == "விருது" or row_key == "விருதுகள்":
                    row_value = get_info_row_texts(row_td)
                    actor['awards'].extend(row_value)
    except Exception:
        print("No info data")

    # Grab data from intro paragraphs
    intro_texts = []
    for tag in soup.find('div', attrs={'class': 'mw-parser-output'}).findChildren(recursive=False):
        if tag.name == 'p':
            for element in tag.find_all('sup', recursive=True):
                element.clear()
            intro_texts.append(tag.get_text().strip())
        elif tag.name != 'p' and tag.name != 'table':
            break
    if len(intro_texts) > 0:
        actor['intro'] = (" ".join(intro_texts)).replace("  ", "")

    # Grab filmography data
    actor['movies'].extend(extract_filmography(soup))

    return actor


def extract_filmography(soup):
    movies = []
    try:
        h2_list = ["திரைப்படங்கள்", "நடிகராக", "திரைப்பட வரலாறு", "திரைப்படவியல்", "இவர் நடித்த சில திரைப்படங்கள்",
                   "தேர்ந்தெடுக்கப்பட்ட திரைப்படவியல்", "நடித்த திரைப்படங்கள்", "திரைப்பட விபரம்",
                   "திரைப்படங்கள் விபரம்", "நடித்த திரைப்படம்", "நடித்த படங்கள்", "படங்கள்", "திரைப்பட பட்டியல்",
                   "திரைப்படப் பட்டியல்", "திரைப்படப்பட்டியல்"]
        headings = soup.find('div', attrs={'class': 'mw-parser-output'}).find_all('h2')
        for h2 in headings:
            for edit_span in h2.find_all('span', attrs={'class': 'mw-editsection'}):
                edit_span.clear()
            h2_text = h2.get_text().strip()
            if h2_text in h2_list:
                next_siblings = h2.find_next_siblings()
                for next_sibling in next_siblings:
                    for edit_span in next_sibling.find_all('span', attrs={'class': 'mw-editsection'}):
                        edit_span.clear()
                if len(next_siblings) > 0:
                    first_sibling = next_siblings[0]
                    if first_sibling.name == "h3" and (first_sibling.get_text() in h2_list or check_text_contains_numbers(first_sibling.get_text())):
                        for tag in next_siblings[1:]:
                            if tag.name == "table":
                                movies.extend(get_movies_from_table(tag))
                            elif tag.name == "ul":
                                movies.extend(get_movies_from_ul(tag))
                            elif (tag.name == "h2" or (tag.name == "h3" and not check_text_contains_numbers(first_sibling.get_text()))) and len(movies) > 0:
                                break
                    elif first_sibling.name == "table":
                        movies.extend(get_movies_from_table(first_sibling))
                    elif first_sibling.name == "ul":
                        for tag in next_siblings:
                            if tag.name == "ul":
                                movies.extend(get_movies_from_ul(tag))
                            elif (tag.name == "h2" or tag.name == "h3") and len(movies) > 0:
                                break
                    elif first_sibling.name == "div" and first_sibling.find('ul') is not None:
                        for next_sibling in next_siblings:
                            if (next_sibling.name == "h2" or next_sibling.name == "h3") and len(movies) > 0:
                                break
                            for tag in next_sibling.find_all('ul'):
                                movies.extend(get_movies_from_ul(tag))
                    elif first_sibling.name == "dl" and next_siblings[1].name == "div" and next_siblings[1].find('ul') is not None:
                        for next_sibling in next_siblings:
                            if (next_sibling.name == "h2" or next_sibling.name == "h3") and len(movies) > 0:
                                break
                            for tag in next_sibling.find_all('ul'):
                                movies.extend(get_movies_from_ul(tag))
                    else:
                        for next_sibling in next_siblings:
                            if next_sibling.name == "div" and next_sibling.get_attribute_list('role')[0] == "note":
                                a_tag = next_sibling.find('a')
                                if a_tag is not None and "நடித்த திரைப்படங்கள்" in a_tag.get_text():
                                    a_tag_href = base_url + a_tag.get('href')
                                    a_tag_req = requests.get(a_tag_href)
                                    a_tag_page = a_tag_req.content
                                    a_tag_soup = BeautifulSoup(a_tag_page, 'html.parser', from_encoding='utf-8')
                                    movies.extend(extract_filmography(a_tag_soup))
    except Exception as e:
        print("No filmography data")
        print("Exception: ", e)

    return movies


def get_movies_from_table(table):
    movies = []
    tbody_rows = table.find('tbody').find_all('tr')
    thead_cols = tbody_rows[0].find_all('th')
    i_year = 0
    i_movie = 0
    th_year = ["ஆண்டு", "வருடம்", "வெளியான நாள்", "வெளியான வருடம்", "வெளியான ஆண்டு"]
    th_movie = ["திரைப்படம்", "படம்"]
    last_rowspan = 0
    last_year = ""
    for i in range(len(thead_cols)):
        if thead_cols[i].get_text().strip() in th_year:
            i_year = i
        elif thead_cols[i].get_text().strip() in th_movie:
            i_movie = i
    for row in tbody_rows[1:]:
        row_tds: List[Tag] = row.find_all('td')
        year = row_tds[i_year].get_text().strip()
        if last_rowspan == 0:
            last_year = year if year.isnumeric() else ""
            match = re.search(r'\d{4}', year)
            movie = {
                'year': year[match.start():match.end()],
                'movie': row_tds[i_movie].get_text().strip().split("\n")[0].strip()
            }
        else:
            last_rowspan -= 1
            movie = {
                'year': last_year,
                'movie': row_tds[i_movie - 1].get_text().strip().split("\n")[0].strip()
            }
        movies.append(movie)
        if len(row_tds) == len(thead_cols):
            rowspan = row_tds[i_year].get_attribute_list('rowspan')[0]
            if rowspan is not None:
                last_rowspan = int(rowspan) - 1
    return movies


def check_text_contains_numbers(text: str):
    return bool(re.search(r'\d{3,8}', text))


def get_movies_from_ul(ul):
    movies = []
    list_li = ul.find_all('li')
    for li in list_li:
        li_texts = list(filter(None, li.get_text().split("(")))
        movie = {
            'movie': li_texts[0].strip().split("\n")[0].strip()
        }
        if len(li_texts) > 1:
            year = li_texts[1].split(")")[0].strip()
            movie['year'] = year if year.isnumeric() else ""
        movies.append(movie)
    return movies


def remove_bracketed_text(text: str):
    text = (text.strip().split("(")[0]).strip()
    return text if not text.isnumeric() else None


def get_info_row_texts(row_td: Tag):
    for br in row_td.find_all('br', recursive=True):
        br.insert(0, ',')
    for li in row_td.find_all('li', recursive=True):
        li.insert(0, ',')
    return list(
        filter(None,
               map(remove_bracketed_text, row_td.get_text().replace(" ", " ").replace("\n", ",").strip().split(","))))


if __name__ == "__main__":
    # # Scrape urls of a list of actors from web page
    # data = scrape_actors_links()
    #
    # # Save urls of actors in a csv file
    # df = pd.DataFrame.from_records(data)
    # df.to_csv('data_actors_links.csv', index=False, encoding='utf-8-sig')

    # Scrape single actor data
    data = scrape_actor_data(
        "https://ta.wikipedia.org/wiki/%E0%AE%A8%E0%AE%BE%E0%AE%95%E0%AF%87%E0%AE%B7%E0%AF%8D")

    # Save single actor data as json file
    with codecs.open('data_actor.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
