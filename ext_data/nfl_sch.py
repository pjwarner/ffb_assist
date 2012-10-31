#!/usr/bin/env python
import os
import requests
import conn as data
from lxml import etree
from StringIO import StringIO

class nfl_schedule():
    def get_sch(self, year, week):
        url = 'http://www.nfl.com/schedules/%s/REG%s' % (year, week)

        week = '%02d' % week
        dirname = 'raw_data/%s/%s' % (year, week)

        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except OSError:
                if os.path.exists(dirname):
                    pass
                else:
                    raise
 
        
        with open(('raw_data/%s/%s/nfl_sch.html' % (year, week)), 'w') as f:
                headers = {
                    'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/420+ (KHTML, like Gecko) Chrome/14.0.835.186 Safari/419.3'
                    }
                    
                r = requests.get(url, headers=headers)
                f.write(r.text)
                return StringIO(r.text)

    def parse_sch(self, html):
        parser = etree.HTMLParser()
        tree = etree.parse(html, parser)

        away = tree.xpath('//div[@class="list-matchup-row-team"]/span[1]')
        home = tree.xpath('//div[@class="list-matchup-row-team"]/span[5]')

        name_convert = self.team_name_dict()
        
        games = {}
        for x in range(len(away)):
            try:
                games[name_convert[away[x].text]] = name_convert[home[x].text]
                games[name_convert[home[x].text]] = name_convert[away[x].text]
            except:
                pass

        return games

    def upd_sch(self, games, year, week):
        year = int(year)
        week = int(week)
        for k,v in games.items():
            sch_info = data.db.nfl_sch.find_one({'YEAR':year, 'WEEK':week, 'TEAM':k, 'OPP':v})
            if not sch_info:
                print('Entering new game')
                data.db.nfl_sch.insert({
                        'YEAR':year,
                        'WEEK':week,
                        'TEAM':k,
                        'OPP':v
                        })
            else:
                print('Updating existing game')
                data.db.nfl_sch.update({
                        'YEAR':year,
                        'WEEK':week,
                        'TEAM':k,
                        'OPP':v
                        }, {'$set':{
                            'YEAR':year,
                            'WEEK':week,
                            'TEAM':k,
                            'OPP':v}})
    
    def team_name_dict(self):
        '''
        Takes a name like Cowboys and returns DAL
        
        '''

        teams = {
            'Broncos': 'DEN',
            'Vikings': 'MIN',
            'Bears': 'CHI',
            'Falcons': 'ATL',
            'Saints': 'NO',
            'Chargers': 'SD',
            'Raiders': 'OAK',
            'Lions': 'DET',
            'Browns': 'CLE',
            'Eagles': 'PHI',
            'Steelers': 'PIT',
            'Giants': 'NYG',
            'Buccaneers': 'TB',
            'Cardinals': 'ARI',
            'Bengals': 'CIN',
            'Chiefs': 'KC',
            'Jaguars': 'JAC',
            'Redskins': 'WAS',
            'Jets': 'NYJ',
            'Ravens': 'BAL',
            'Colts': 'IND',
            'Packers': 'GB',
            'Dolphins': 'MIA',
            'Titans': 'TEN',
            'Rams': 'STL',
            'Bills': 'BUF',
            'Texans': 'HOU',
            '49ers': 'SF',
            'Patriots': 'NE',
            'Cowboys': 'DAL',
            'Seahawks': 'SEA',
            'Panthers': 'CAR'
            }
        return teams

if __name__ == '__main__':
    year = 2012
    week = 8
    a = nfl_schedule()
#    for week in range(8,18):
    html = a.get_sch(year, week)
    games = a.parse_sch(html)
    a.upd_sch(games, year, week)
