'''
Module that take the scraped jsons in the data directory, converts them in Models and save them in the database 
'''

from models import Match, Team, Championship, db
import json
import datetime


def load_championship(year):
    '''
        Load all the games in the championship year/year+1 and saves it in the database
    '''
    # Load the championship. If it does not exists creates it
    dbchampionship, created = Championship.get_or_create(startyear=year)
    with open(f'data/championship{year}.json') as json_file:
        days = json.load(json_file)
    for day in days:
        n = day.get("number")
        date = datetime.datetime(day['date']['year'],
                                 day['date']['month'],
                                 day['date']['day'])
        for match in day['matches']:
            # Create a match
            dbmatch = Match(date=date, championship=dbchampionship, number=n)
            dbmatch.results_from_dict(match)
            dbmatch.save()
        print(f"{n}th day of championship {dbchampionship} done.")


if __name__ == "__main__":
    db.connect()
    db.create_tables([Team, Championship, Match])
    for i in range(1986, 2021):
        load_championship(i)
