from pymongo import MongoClient


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
        
        return {matchup['start_id']: get_players(matchup)
                                     for matchup in self.game['matchups']}

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
        event_list.append(event['PCTIMESTRING'])
        event_list.append(event['EVENTMSGTYPE'])
        event_list.extend([event['PLAYER1_ID'], event['PLAYER1_NAME']])
        event_list.extend([event['PLAYER2_ID'], event['PLAYER2_NAME']])
        event_list.append(event['HOMEDESCRIPTION'] if event['HOMEDESCRIPTION'] \
                                                   else event['VISITORDESCRIPTION'])
        return event_list

    def _update_current_players(self, event):
        """Turn an event dictionary into a list that's better for putting in a dataframe.

        Parameters
        ----------
        event : dict
        """
        player_1_idx = self._current_players.index(event['PLAYER1_ID'])
        sub_player_info = event['PLAYER2_ID'], event['PLAYER2_NAME']
        self._current_players[player_1_idx:player_1_idx+2] = sub_player_info


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
            return event['PCTIMESTRING']

    events = game['_playbyplay']['resultSets']['PlayByPlay']
    for event in events:
        if not only_event_type or event['EVENTMSGTYPE'] == only_event_type:
            description = make_description(event)
            print('{: <3} :: {: <70} Type = {: <2} Period = {}'.format(
                   event['EVENTNUM'], description,
                   event['EVENTMSGTYPE'], event['PERIOD']))
            inpt = input()
            if inpt == 'i':
                print(event)
                print('\n')
            elif inpt == 'q':
                break


if __name__ == '__main__':
    client = MongoClient()
    games_col = client.bball.games
    test_game = games_col.find()[0]
