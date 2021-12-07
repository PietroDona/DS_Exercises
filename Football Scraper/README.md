# FootballScraper

The project is made of 3 parts

## A scrapy spider
`seriea/spiders/match_spider.py`
The spider that scrapes the historic data of the Italian football Serie A league from the official website `www.legaseriea.it` 

`scrape` 
A bash script that runs the spider for all the available years (from 1986-87 to 2020-21)

`data/`
The default directory where the data is stored

## A ORM interface to a sqlite database
`models.py`
Module with a peewee interface to the scraped data. 

`jsontodb.py`
Module that parse the json produced by the spider and store the data in a sqlite database. Default `data/serieA.db`

## An example notebook
`analysis.ipynb`
Example notebook that load the database data, converts it in pandas dataframe and performs some basic operations.

## Requirements
The scripts need, [scrapy](https://scrapy.org/) and [peewee](http://docs.peewee-orm.com/en/latest/index.html) to create the database. The notebook also needs [pandas](https://pandas.pydata.org/) and [seaborn](https://seaborn.pydata.org/).

## Quickstart
Crawl the spider using the bash script 

`./scrape`

Load the jsons in `data/` in the database `data/serieA.db` running

`python jsontodb.py`

Profit. See the example notebook `analysis.ipynb` to see how to load the data from the database in a dataframe.

TODO: Use scrapy item system ORM to iterface with sqlite db
