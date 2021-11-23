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
