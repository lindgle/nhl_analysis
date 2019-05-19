# -*- coding: utf-8 -*-
"""
Created on Mon May  6 20:16:28 2019

@author: Leevi
"""

import pandas as pd
import urllib.request, json 

class NHLapi():
    '''
    Class to stab NHL stats api
    '''
    def __init__(self, apiurl='https://statsapi.web.nhl.com/api/v1/'):
        self.apiurl = apiurl
        self.games = None # Game data
        self.teams = None # Teams
        
    def get_games(self, start='2019-05-01', end='2019-05-09'):
        assert start is not None, 'Start date is not valid'
        assert end is not None, 'End date is not valid'
        
        url = (
                self.apiurl + 'schedule?' + 
               'startDate=' + start + '&endDate=' + end
               ) 
        with urllib.request.urlopen(url) as json_file:
            data = json.loads(json_file.read().decode())
            data = data['dates']
            
        n_match_days = len(data)
        
        game_id = []
        game_type = []
        season = []
        game_date = []
        home_team = []
        away_team = []
        home_score = []
        away_score = []
        status = []
        
        for i in range(n_match_days):
            match_day = data[i]            
            n_matches = len(match_day['games'])            
            
            for j in range(n_matches):
                game = match_day['games'][j]
                ht = game['teams']['home']['team']['id']
                at = game['teams']['away']['team']['id']
                
                hsc = game['teams']['home']['score']
                asc = game['teams']['away']['score']
                
                game_id.append(game['gamePk'])
                game_type.append(game['gameType'])
                season.append(game['season'])
                game_date.append(game['gameDate'])
                home_team.append(ht)
                away_team.append(at)
                home_score.append(hsc)
                away_score.append(asc)
                status.append(game['status']['detailedState'])
        
        df = pd.DataFrame({'game_id': game_id,
                          'game_type': game_type,
                          'season': season,
                          'game_date': game_date,
                          'home_team': home_team,
                          'away_team': away_team,
                          'home_team_score': home_score,
                          'away_team_score': away_score,
                          'status': status
                          })
        return df
        
    def get_teams(self):
        url= self.apiurl + 'teams/'
        with urllib.request.urlopen(url) as json_file:
            data = json.loads(json_file.read().decode())
            data = data['teams']
        
        n_teams = len(data)
        
        team = []
        team_name = []
        link = []
        division = []
        conference = []
        
        for i in range(n_teams):
            team.append(data[i]['id'])
            team_name.append(data[i]['name'])
            link.append(data[i]['link'])
            division.append(data[i]['division']['id'])
            conference.append(data[i]['conference']['id'])
        
        df = pd.DataFrame({'team_id_original': team,
                           'team_name': team_name,
                           'link': link,
                           'division': division,
                           'conference': conference
                           })
        df['team_id'] = df['team_id_original'].rank().astype('int64')    
    
        return df
        
    def get_standings(self, season=20182019, date=None):
        url = self.apiurl + 'standings'
        if date is None:
            url = url + '?season=' + str(season)
        
        with urllib.request.urlopen(url) as json_file:
            data = json.loads(json_file.read().decode())
        data = data['records']
        
        teams = []
        points = []
        
        for division in range(len(data)):     
            team_records = data[division]['teamRecords']
            for k in range(len(team_records)):
                team = team_records[k]['team']['id']
                point = team_records[k]['points']
                
                teams.append(team)
                points.append(point)
        
        df = pd.DataFrame({'team_id_original': teams,
                           'points': points
                           })
        df['season'] = season
        
        return df.sort_values('points', ascending=False).reset_index(drop=True)
            
