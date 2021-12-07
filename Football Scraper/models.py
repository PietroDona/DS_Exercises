'''
Module that defines the models to interface the peewee ORM with the SQLite database and basic methods
'''

from peewee import IntegerField, SqliteDatabase, Model
from peewee import CharField, DateField, ForeignKeyField


# Main database
db = SqliteDatabase('data/serieA.db')


class Team(Model):
    '''
    Model that represent a team.
        name: name of the team

        team_matches_all() queryset of all the matches of the team
    '''

    class Meta:
        database = db  # This model uses the "people.db" database.

    name = CharField()

    def team_matches_all(self):
        return (self.team_matches_home +
                self.team_matches_guest).order_by(Match.date)

    def __str__(self):
        return self.name


class Championship(Model):
    '''
    Model that represent a championship.
        startyear: year when the championship started
        endyear: year when the championship ended
        playing_teams: queryset of teams that took part to the championship
        compute_ranking(): queryset of the stats of every team that took part in the championship
    '''

    class Meta:
        database = db  # This model uses the "people.db" database.

    startyear = IntegerField()

    @property
    def endyear(self):
        return self.startyear + 1

    @property
    def playing_teams(self):
        return Team.select().join(Match, on=(Match.team1 == Team.id)).where(
            Match.championship == self).distinct()

    def compute_ranking(self):
        for team in self.playing_teams:
            played_matches = self.championship_matches.where(
                (Match.team1 == team) | (Match.team2 == team))
            yield get_results(team, played_matches)

    def __str__(self):
        return f"{self.startyear}-{self.endyear % 100}"


def get_results(team, played_matches):
    '''
    stats of the team in the played_matches
    '''
    points, wins, even, scored, taken = 0, 0, 0, 0, 0
    for m in played_matches:
        if m.winner == team:
            points += 3
            wins += 1
        if m.winner is None:
            points += 1
            even += 1
        if m.team1 == team:
            scored += m.team1goals
            taken += m.team2goals
        else:
            taken += m.team1goals
            scored += m.team2goals

    return {'team': team.name,
            'points': points,
            'played': len(played_matches),
            'won': wins,
            'even': even,
            'lost': len(played_matches)-wins-even,
            'scored': scored,
            'taken': taken}


class Match(Model):
    '''
    Model that represent a match.
        championship: the match is part of this championship
        date: indicative date of the match
        number: number of the game relative of the championship
        team1/team2: teams that took part in the match. team1 is the home team, team2 is the guest team
        team1goals/team2goals: number of goals scored by team1/2

        winner: team that won the match, None if it is a draw
        results_from_dict(dictionary): method to load the detail of the match from a dictionary

    '''

    class Meta:
        database = db  # This model uses the "people.db" database.

    championship = ForeignKeyField(
        Championship, backref='championship_matches')
    date = DateField()
    number = IntegerField()
    team1 = ForeignKeyField(Team, backref='team_matches_home')
    team2 = ForeignKeyField(Team, backref='team_matches_guest')
    team1goals = IntegerField()
    team2goals = IntegerField()
    # TODO: add JSON field with the scorers

    @property
    def winner(self):
        if self.team1goals < self.team2goals:
            return self.team2
        if self.team1goals == self.team2goals:
            return None
        if self.team1goals > self.team2goals:
            return self.team1

    def results_from_dict(self, dictionary):
        # Create the teams if they don't exists
        team1, _ = Team.get_or_create(
            name=dictionary["team1"]["name"])
        team2, _ = Team.get_or_create(
            name=dictionary["team2"]["name"])
        self.team1 = team1
        self.team1goals = dictionary["team1"]["goals"]
        self.team2 = team2
        self.team2goals = dictionary["team2"]["goals"]

    def __str__(self):
        return f"{self.team1} vs {self.team2} the {self.date.day}/{self.date.month}/{self.date.year}"


if __name__ == '__main__':
    '''
    Create the tables in the database (does nothing if they exists)
    '''
    db.connect()
    db.create_tables([Team, Championship, Match])
