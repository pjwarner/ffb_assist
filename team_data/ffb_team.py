#!/usr/bin/env python
import requests
from StringIO import StringIO
from lxml import etree

class fantasy_team():
    def get_players(self):
        '''
        Generate a URL for fetching html page that has the player data
        '''
        raise NotImplementedError
    
    def parse_players(html):
        '''
        from the HTML gernate and return the players dict. Should contain:
          _id : team_pos_name,
          NAME : name,
          POS: pos,
          TEAM: team
        '''
        raise NotImplementedError

    def return_players(self):
        '''
        Returns a standardized dict to calling method:

        {
          _id:team_pos_name,
          NAME: name,
          POS: pos,
          TEAM, team
        }
        '''
        raise NotImplementedError
    
class nfl(fantasy_team):
    def get_players(self, league, team_id, debug=False):
        url = "http://fantasy.nfl.com/league/%s/team/%s" % (league, team_id)
        headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) Apple WebKit/420+ (KHTML, like Gecko) Chrome/14.0.835.186 Safari/419.3'
            }
                
        r = requests.get(url, headers=headers)

        if debug:
            with open('test_data/ffb_team.html', 'w') as f:
                f.write(r.text)

        return StringIO(r.text)

    def parse_players(self, html):
        parser = etree.HTMLParser()
        tree = etree.parse(html, parser)

        player_entries = tree.xpath('//div[@class="tableWrap"]/table/tbody/tr')

        players = {}
        for x in range(len(player_entries) + 1)[1:]:
            try:
                name = tree.xpath('//div[@class="tableWrap"]/table[1]/tbody[1]/tr[%i]/td[@class="playerNameAndInfo"]/div/a[1]'% (x))[0].text
                (pos, team) = tree.xpath('//div[@class="tableWrap"]/table[1]/tbody[1]/tr[%i]/td[@class="playerNameAndInfo"]/div/em[1]' % (x))[0].text.split(' - ')

                players[x] = {
                    '_id' : team + '_' + pos + '_' + name.replace(' ','_'),
                    'NAME': name,
                    'POS': pos,
                    'TEAM': team
                    }
            except:
                pass #need to log this info later?
        return players

    def return_players(self, league, team_id, debug=False):
        html = self.get_players(league, team_id, debug)
        players = self.parse_players(html)
        return players
    
class yahoo(fantasy_team):
    pass

class espn(fantasy_team):
    pass

class test():
    def nfl(self, league, team_id, debug=True):
        '''
        testing data actually ON nfl.com
        '''
        
        p = nfl()
        players = p.return_players(league, team_id, debug)
        for x in players: print players[x]['NAME']

    def dev(self):
        '''
        currently testing data written to test_data/ffb_team.html
        '''
        p = nfl()
        with open('test_data/ffb_team.html', 'r') as f:
            players = p.parse_players(f.name)

        return players
        

if __name__ == '__main__':
    t = test()
    #t.nfl(592090, 3, True)
    a = t.dev()
    for x in a: print a[x]['_id']
