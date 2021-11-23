# Tamil Actors Search Engine
 
This repository contains the source code of Tamil Actors Search Engine implemented using Python and Elasticsearch.

## Directory Structure

 ├── analyzers : Custom Elasticsearch filters (Stems, Stopwords, Synonyms)
 ├── data : Data scraped from the website (https://ta.wikipedia.org/)
     ├── data_actors.json : Contains all scraped data of actors
     ├── data_actors_links.csv : Contains web urls of actors to scrape data from.
     ├── data_actors_with_info.json : Contains scraped data of actors having non-null 'date_of_birth'
     ├── data_actors_with_movies.json : Contains scraped data of actors having non-empty 'movies'
     ├── data_actors_with_info_movies.json : Contains scraped data of actors having both non-null 'date_of_birth' and non-empty 'movies'
 ├── app : Frontend of the web app (works for basic search querying)
 ├── app.py : Backend of the web app created using Flask
 ├── data_uploading.py : Python file to convert JSON data to bulkdata, and upload to Elasticsearch Bulk API
 ├── query_searching.py : Search API functions
 ├── requirements.txt : Python dependencies required for the project
 ├── search_queries.txt : Example search queries
 ├── setup_queries.txt : Some queries to setup the elasticsearch "tamilactors" index
 ├── web_scraping.py : Python file to scrape data, preprocess and store them in a JSON file
