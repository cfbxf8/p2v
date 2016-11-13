from pymongo import MongoClient
import pandas as pd
import json


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


class ParseGameJSON():
    def __init__(self, game):
        self.game = game
        self.plays = []
        self._no_play = 'no_play'
        self._no_play_events = {8, 12, 13}
        self._players = self._make_players_dict()
        self._current_players = self._players[0]
        self._parse_plays()

    def _make_players_dict(self):
        """Makes dictionary of players on the court.

        Returns
        -------
        {event_num: [id, name] * 10}
        """
        def get_players(matchup):
            """Helper function to make player list from matchup.
            """
            home_players = [p[attr] for p in matchup['home_players'][0]
                                    for attr in ['id', 'name']]
            away_players = [p[attr] for p in matchup['away_players'][0]
                                    for attr in ['id', 'name']]
            return home_players + away_players

        return {mu['start_id']: get_players(mu) for mu in self.game['matchups']}

    def _parse_plays(self):
        """Turn a game dictionary in to a list of lists. Appends information
        from game events to plays attribute.
        """
        events = self.game['_playbyplay']['resultSets']['PlayByPlay']
        for event in events:
            play = self._parse_event(event)
            if play == self._no_play:
                continue
            self.plays.append(play)

    def _parse_event(self, event):
        """Turn an event dictionary into a list that's better for putting
        in a dataframe.

        Parameters
        ----------
        event : dict
        """
        if event['EVENTMSGTYPE'] in self._no_play_events:
            self._current_players = self._players.get(event['EVENTNUM'],
                                                      self._current_players)
            return self._no_play

        event_list = [event['EVENTNUM']] + self._current_players[:]
        event_list.append(event['PERIOD'])
        event_list.append(event['PCTIMESTRING'])
        event_list.append(event['EVENTMSGTYPE'])
        event_list.append(EVENT_DICT.get(event['EVENTMSGTYPE'], 'unknown_key'))
        event_list.extend([event['PLAYER1_ID'], event['PLAYER1_NAME']])
        event_list.extend([event['PLAYER2_ID'], event['PLAYER2_NAME']])
        event_list.append(event['HOMEDESCRIPTION'] if event['HOMEDESCRIPTION'] \
                                                   else event['VISITORDESCRIPTION'])
        return event_list

    def to_df(self):
        """Turn parsed game json into a data frame.
        """
        play_columns = ['event_num', 'home_p1_id', 'home_p1_name',
                        'home_p2_id', 'home_p2_name', 'home_p3_id',
                        'home_p3_name', 'home_p4_id', 'home_p4_name',
                        'home_p5_id', 'home_p5_name', 'away_p1_id',
                        'home_p1_name', 'home_p2_id', 'home_p2_name',
                        'home_p3_id', 'home_p3_name', 'home_p4_id',
                        'home_p4_name', 'home_p5_id', 'home_p5_name',
                        'period', 'clock', 'event_num', 'event_type',
                        'active_p1_id', 'active_p1_name', 'active_p2_id',
                        'active_p2_name', 'play_description']
        return pd.DataFrame(self.plays, columns=play_columns)


def view_plays(game, only_event_type=None):
    """Helper function to inspect what the data in a game looks like.

    Parameters
    ----------
    game : dict
    only_event_type : int - only show this event type
    """
    def make_description(event):
        """Helper function to handling interactive printing.
        """
        if event['VISITORDESCRIPTION']:
            return event['VISITORDESCRIPTION']
        elif event['HOMEDESCRIPTION']:
            return event['HOMEDESCRIPTION']
        else:
            return 'No description'

    events = game['_playbyplay']['resultSets']['PlayByPlay']
    for event in events:
        if not only_event_type or event['EVENTMSGTYPE'] == only_event_type:
            description = make_description(event)
            print('{: <3} :: {: <65} Type: {: <2} - Period: {} - Time: {}'
                  .format(event['EVENTNUM'], description, event['EVENTMSGTYPE'],
                          event['PERIOD'], event['PCTIMESTRING']))
            inpt = input()
            if inpt == 'i':
                print(json.dumps(event, indent=1, sort_keys=True))
            elif inpt == 'q':
                break


if __name__ == '__main__':
    client = MongoClient()
    games_col = client.bball.games
    test_game = games_col.find()[0]
