# Tamil Actors Search Engine
 
This repository contains the source code of Tamil Actors Search Engine implemented using Python and Elasticsearch.

## Directory Structure
```
 ├── analyzers : Custom Elasticsearch filters (Stems, Stopwords, Synonyms)
 ├── data : Data scraped from the website (https://ta.wikipedia.org/)
     ├── data_actors.json : Contains all scraped data of actors
     ├── data_actors_links.csv : Contains web urls of actors to scrape data from.
     ├── data_actors_with_info.json : Contains scraped data of actors having non-null 'date_of_birth'
     ├── data_actors_with_movies.json : Contains scraped data of actors having non-empty 'movies'
     ├── data_actors_with_info_movies.json : Contains scraped data of actors having both non-null 'date_of_birth' and non-empty 'movies'
 ├── app : Frontend of the web app
 ├── app.py : Backend of the web app created using Flask
 ├── data_uploading.py : Python file to convert JSON data to bulkdata, and upload to Elasticsearch Bulk API
 ├── query_searching.py : Search API functions
 ├── requirements.txt : Python dependencies required for the project
 ├── search_queries.txt : Example search queries
 ├── setup_queries.txt : Some queries to setup the elasticsearch "tamilactors" index
 ├── web_scraping.py : Python file to scrape data, preprocess and store them in a JSON file
```

## Getting started
* Clone the repo and install the required Python dependencies.
  ```commandline
  git clone https://github.com/thuvarahan97/Tamil-Actors-Search.git
  cd Sinhala Songs Search
  virtualenv -p python3 envname
  source env/bin/activate
  pip3 install -r requirements.txt
  ```
* Download and install [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/getting-started-install.html)
* Create 'analyze' folder inside the config folder of Elasticsearch and copy files from analyzers.
* Create index "tamilactors" in Elasticsearch along with Custom filters (refer "Custom stemmer, stopper and synonyms" section in the [setup_queries.txt](/setup_queries.txt) file) using [Postman](https://www.postman.com/downloads/).
* Add mapping to "tamilactors" Elasticsearch index (refer "Aggregation" section in the [setup_queries.txt](/setup_queries.txt) file) using [Postman](https://www.postman.com/downloads/).
* If you want to scrape new data, run ```python web_scraping.py``` in a terminal.
* Start the elasticsearch.
* Run ```python data_uploading.py``` to upload data to the Elasticsearch index "tamilactors" in a terminal.
* Run ```python app.py``` in a terminal.
* Go to http://127.0.0.1:5000/
* Search for actors (Works only for basic search queries at the moment using this web app)
* For advanced queries, try the search queries available in the [search_queries.txt](/search_queries.txt) file using [Postman](https://www.postman.com/downloads/) or [Kibana](https://www.elastic.co/kibana/).

## Data
The data have been scraped in **Tamil** language from the Wikipedia website [https://ta.wikipedia.org/w/index.php?title=பகுப்பு:தமிழ்த்_திரைப்பட_நடிகர்கள்](https://ta.wikipedia.org/w/index.php?title=பகுப்பு:தமிழ்த்_திரைப்பட_நடிகர்கள்) using the HTML/XML parsing library BeautifulSoup. This web page contains a list of names of tamil actors under the section "தமிழ்த் திரைப்பட நடிகர்கள்" பகுப்பிலுள்ள கட்டுரைகள் in which each name contains a web link to the main page of the actor. 

## Data fields 
Each actor contains the following data fields.
1. name - Name of the actor
2. date_of_birth - Date of birth of the actor
3. date_of_death - Date of death of the actor (if the actor is already dead)
4. place_of_birth - Place of birth of the actor
5. spouse - List of spouse of the actor
6. children - List of children of the actor
7. movies - List of movies acted by the actor
   <br/>(for each movie in the list)
   1. year - Release year of the movie
   2. movie - Name of the movie
8. other_occupations - List of occupations carried out by the actor other than acting
9. awards - List of awards received by the actor
10. description - Description of the actor

## SampleQueries
* Search for actors by any of the listed data fields.
 > E.g.- "கமல்ஹாசன்"
```
{
    "query": {
        "query_string": {
            "query":"கமல்ஹாசன்"
        }
    }
}
```

* Search for actors specifying the field when you just know any of the listed data fields.
 > E.g.- "விருது பத்மஸ்ரீ"
```
{
     "query" : {
          "match" : {
             "awards" : "பத்மஸ்ரீ"
         }
     }
}
```
* Search with WildCard when you are not sure about the spelling of the word.
 > E.g.- "கமல்*" for "கமல்ஹாசன்"
```
{
     "query" : {
          "wildcard" : {
              "name" : "கமல்*"
         }
     }
}
```
* Search when you think one term might show up in multiple fields
 > E.g.- "தேசிய விருது"
```
{
    "query" : {
        "multi_match" : {
            "query" : "தேசிய விருது",
            "fields": ["awards", "description"]
        }
    }
}
```
* Search for 20 young actors who are directors where young is decided based on "date_of_birth"
 > E.g. - 20 இளைய இயக்குநர்
```
{
   "size": 20,
   "sort": [
       { "date_of_birth": {"order" : "desc"}}
   ],
   "query": {
       "multi_match": {
           "fields":["other_occupations"],
           "query" : "இயக்குநர்",
           "fuzziness": "AUTO"
       }
   }
}
```
* Search for actors who acted in year 2020 (Nested query)
 > E.g. - 2020 ஆம் ஆண்டில் நடித்த நடிகர்
```
{
    "query": {
        "nested" : {
            "path" : "movies",
            "score_mode" : "avg",
            "query" : {
                "bool" : {
                  "must" : [
                      { "match" : {"movies.year" : "2020"} }
                    ]
                }
            }
        }
    }
}
```
* Search with query spanning multiple fields
 > E.g.- சிறந்த நடிகர் விருது பெற்ற தமிழ்நாடு நடிகர்
```
{
    "query": {
        "bool": {
             "must": [
                 { "match": { "awards": "சிறந்த நடிகர் விருது" }},
                 { "match": { "place_of_birth": "தமிழ்நாடு" }}
             ]
        }
    }
}
```
* Seach for actors who are singers died recently (Range Query) where died recently is based on "date_of_death"
 > E.g.- சமீபத்தில் இறந்த பாடகர்
```
{
    "query": {
        "bool": {
            "must": [
                {
                    "match": {
                        "other_occupations": "பாடகர்"
                    }
                },
                {
                    "range": {
                        "date_of_death" : {
                            "gte" : "2021"
                        }
                    }
                }
            ]
        }
    }
}
```
* Search for actors who are lyricists and were born in Chennai (Filtered query)
 > E.g. - சென்னை பாடலாசிரியர்
```
{
  "query": {
    "bool": {
      "must": {
        "match": {
          "other_occupations": "பாடலாசிரியர்"
        }
      },
      "filter": {
        "term": {
          "place_of_birth": "சென்னை"
        }
      }
    }
  }
}
```
* Get only prefered fields when searching with other field
> E.g.- 20 இளைய இயக்குநர் துணைவர்/பிள்ளைகள்
 * 
```
{
   "size": 20,
   "sort": [
       { "date_of_birth": {"order" : "desc"}}
   ],
   "query": {
       "multi_match": {
           "fields":["other_occupations"],
           "query" : "இயக்குநர்",
           "fuzziness": "AUTO"
       }
   },
   "_source":{
       "includes":["spouse", "children"]
   }
}
```
* Search for details only with description of actors (Text Mining)
```
{
  "query": {
    "more_like_this": {
      "fields": [
        "description"
      ],
      "like": "தமிழ்நாட்டு மாதிரி நடிகர், குறும்பட நடிகர் மற்றும் தொலைக்காட்சி நடிகர். சிறப்பாக நடித்ததற்காக சிறந்த துணை நடிகருக்கான இந்திய தேசிய திரைப்பட விருது கிடைத்தது.",
      "min_term_freq": 1,
      "max_query_terms": 20
    }
  }
}
```
* Can do aggregated bucket querying with terms
```
{
  "aggs": {
    "Occupations": {
      "terms": {
        "field": "other_occupations",
        "size": 10
      }
    }
  }
}
```
