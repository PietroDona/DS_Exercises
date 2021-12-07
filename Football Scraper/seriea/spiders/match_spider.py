import scrapy
from datetime import datetime
import re


class ChampionshipSpider(scrapy.Spider):
    '''
        Scrapy Spider that scraps the results of the SerieA (italian premier league) from the archive of the official website
            match is the name of the spider
            y is the year we want to scrape passed as an argument
        The usage is
            scrapy crawl match -a year=1996 -O data/championship1996.json
    '''
    name = "match"
    y = None

    def find_max_days(self, year):
        '''
        Until 1987-88 the championship had 30 games
        Between 1988-89 and 2003-04 the championship had 34 games
        Modern championships have 38 games
        '''
        if year < 1988:
            return 30
        if year < 2004:
            return 34
        return 38

    def __init__(self, year=1986, *args, **kwargs):
        '''
        Initialization of the spider and the year
        '''
        super(ChampionshipSpider, self).__init__(*args, **kwargs)
        self.y = int(year)

    def start_requests(self):
        '''
            Definition of the scrape urls and request parsing
        '''
        urls = [
            f"https://www.legaseriea.it/it/serie-a/archivio/{self.y:02d}-{(self.y+1)%100:02d}/UNICO/UNI/{i}" for i in range(1, self.find_max_days(self.y)+1)]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        '''
            Parsing function that retrive the match number, date, a list of matches with scores and scorers
        '''
        title = response.css('section.risultati h3::text').get().strip()
        number, date = title.split("-")
        refyear = response.request.url.split("/")[-4]
        date = datetime.strptime(date.strip(), '%d/%m/%Y')
        number = int(re.findall(r'\d+', number)[0])

        matches = [self.parse_game(game) for game in response.css(
            'section.risultati div.box-partita')]

        yield {'number': number,
               'date': {'day': date.day,
                        'month': date.month,
                        'year': date.year},
               'refyear': int(refyear.split("-")[0]),
               'matches': matches,
               }

    def parse_game(self, game):
        '''
            Extract the match infos from the game box (div)
        '''
        sx = game.css('div.risultatosx')
        teamsx = sx.css('h4.nomesquadra::text').get().strip()
        goalssx = int(sx.css('span::text').get().strip())
        scorerssx = [player.strip() for player in sx.css(
            'p.marcatori-partita::text').getall() if player.strip() != '']

        dx = game.css('div.risultatodx')
        teamdx = dx.css('h4.nomesquadra::text').get().strip()
        goalsdx = int(dx.css('span::text').get().strip())
        scorersdx = [player.strip() for player in dx.css(
            'p.marcatori-partita::text').getall() if player.strip() != '']

        return {'team1': {'name': teamsx,
                          'goals': goalssx,
                          'scorers': scorerssx},
                'team2': {'name': teamdx,
                          'goals': goalsdx,
                          'scorers': scorersdx}}
