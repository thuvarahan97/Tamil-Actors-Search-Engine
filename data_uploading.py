import json
import re

from elasticsearch import Elasticsearch, helpers


def read_actors_data(filepath):
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        actors = json.loads(f.read())
        return actors


def format_text(text):
    if text is None or text.strip() == "":
        return None
    return text.strip()


def format_movie(movie):
    if movie['movie'] is None or movie['movie'].strip() == "":
        return None
    else:
        movie['year'] = format_text(movie['year'])
        movie['movie'] = format_text(movie['movie'])
    return movie


def format_date(date):
    if date is not None and date != "":
        date = date.replace(" ", "").strip(" ").strip()
        if len(date) > 4:
            date_splitted = list(date.split("-"))
            if int(date_splitted[1]) > 12:
                return date_splitted[0] + "-" + date_splitted[2] + "-" + date_splitted[1]
    return date


def format_name(name):
    if name is not None and name != "":
        if bool(re.search(r'\d{1,10}', name)):
            return None
    return format_text(name)


def generate_data(actors):
    for actor in actors:
        name = actor.get("name", None)
        date_of_birth = format_date(format_text(actor.get("date_of_birth", "")))
        date_of_death = format_date(format_text(actor.get("date_of_death", "")))
        place_of_birth = format_text(actor.get("place_of_birth", None))
        spouse = list(filter(None, map(format_name, actor.get("spouse", []))))
        children = list(filter(None, map(format_name, actor.get("children", []))))
        movies = list(filter(None, map(format_movie, actor.get("movies", []))))
        other_occupations = list(filter(None, map(format_text, actor.get("other_occupations", []))))
        awards = list(filter(None, map(format_text, actor.get("awards", []))))
        description = format_text(actor.get('intro', None))

        yield {
            "_source": {
                "name": name,
                "date_of_birth": date_of_birth,
                "date_of_death": date_of_death,
                "place_of_birth": place_of_birth,
                "spouse": spouse,
                "children": children,
                "movies": movies,
                "other_occupations": other_occupations,
                "awards": awards,
                "description": description
            },
        }


if __name__ == '__main__':
    client = Elasticsearch(HOST="http://localhost", PORT=9200)
    index = "tamilactors"

    # Read data from json file
    data = read_actors_data("data/data_actors.json")

    # Upload data to elasticsearch
    helpers.bulk(client, generate_data(data), index=index)
