from pymongo import MongoClient


'''Notes
* Successful 3 pointers are fg (1) but say '3PT' in them
* Dunks are fg (1), but say 'Dunk' in them
* Both offensive and defensive rebounds are coded 5. Only way to determine
    which one is by looking at the diff on '(Off: #, Def:#)' which corresponds
    to that player at that point in the game. This will be a pain...
* Quarter is stored under the 'PERIOD' key in each event.
* The person who is fouled (6) is listed under player 2
'''

EVENT_DICT = {1: 'Field Goal',
              2: 'Missed FG',
              3: 'Free throw',
              4: 'Rebound',
              5: 'Turnover',
              6: 'Foul',
              7: 'Violation',
              8: 'Substitution',
              9: 'Timeout',
              10: 'Jump Ball',
              11: 'Ejection',
              12: 'Period Start',
              13: 'Period End'}


def make_play_list(game):
    """Turn a game dictionary in to a list of dictionaries.

    Parameters
    ----------
    game : dict - lots of nested stuff...

    Returns
    -------
    List of lists - inner list represents play.
    """
    players = make_starting_players(game)
    events = game['_playbyplay']['resultSets']['PlayByPlay']
    plays = []
    for event in events:
        play = parse_event(players, event)
        if play:
            plays.append(play)
    return plays


def make_starting_players(game):
    """Makes list of starting player id-name tuples.

    Parameters
    ----------
    game : dict - lots of nested stuff...

    Returns
    -------
    [[id, name]]
    """
    home_starters = [[p['id'], p['name']] for p in game['home_starters']]
    away_starters = [[p['id'], p['name']] for p in game['away_starters']]
    return home_starters + away_starters 


def parse_event(players, event):
    """Turn an event dictionary into a list that's better for putting in a dataframe.

    Parameters
    ----------
    players : list - [[id, name]], current players at start of event
    event : dict
    """
    event_list = [attr for player in players for attr in player]
    event_list.append(event['PCTIMESTRING'])
    event_list.append(event['EVENTMSGTYPE'])
    event_list.extend([event['PLAYER1_ID'], event['PLAYER1_NAME']])
    event_list.extend([event['PLAYER2_ID'], event['PLAYER2_NAME']])
    event_list.append(event['HOMEDESCRIPTION'] if event['HOMEDESCRIPTION'] \
                                               else event['VISITORDESCRIPTION'])
    return event_list


def view_plays(game):
    """Helper function to inspect what the data in a game looks like.
    
    Parameters
    ----------
    game : dict
    """
    events = game['_playbyplay']['resultSets']['PlayByPlay']
    for event in events: 
        description = event['HOMEDESCRIPTION'] if event['HOMEDESCRIPTION'] \
                                               else event['VISITORDESCRIPTION']
        print('{} - {}'.format(description, event['EVENTMSGTYPE']))
        if input() == ' ':
            print(event)
            print('\n')


if __name__ == '__main__':
    client = MongoClient()
    games_col = client.bball.games
