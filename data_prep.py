from pymongo import MongoClient


def make_play_dicts(game):
    """Turn a game dictionary in to a list of dictionaries.

    Parameters
    ----------
    game : dict - lots of nested stuff...

    Returns
    -------
    [{'players': [(id, name)], 'outcome': TODO}]
    """
    players = make_starting_players(game)
    events = game['_playbyplay']['resultSets']['PlayByPlay']
    plays = []
    for event in events:
        play = parse_event(players, event)
        if play:
            plays.append(play)

def make_starting_players(game):
    """Makes list of starting player id-name tuples.

    Parameters
    ----------
    game : dict - lots of nested stuff...

    Returns
    -------
    [(id, name)]
    """
    home_starters = [(p['id'], p['name']) for p in game['home_starters']]
    away_starters = [(p['id'], p['name']) for p in game['away_starters']]
    return home_starters + away_starters 


def parse_event(event, players):
    """
    """
    pass


if __name__ == '__main__':
    client = MongoClient()
    games_col = client.bball.games
