#!/usr/bin/env python
import os
import requests
import conn as data
from lxml import etree
from decimal import Decimal

class Players():
    def dl_stats_nfl(self, year, week, league='592090'):
        '''
        args (int(year), int(week)

        Parse Weekly Player Stats from NFL.com
        Parses the first 25 pages (500 players) of stats. Stats are a weekly
        piece of information.
        '''
        urls = []
        for offset in range(1, 477, 25):
            url = 'http://fantasy.nfl.com/league/' + league + '/players?'
            offset = 'offset=%s&' % offset
            playerStatus = 'playerStatus=all&'
            position = 'position=O&'
            sort = 'sort=pts&'
            statCat = 'statCategory=stats&'
            statSeason = 'statSeason=%s&' % year
            statType = 'statType=weekStats&'
            statWeek = 'statWeek=%s' % week
            
            urls.append(''.join([url, offset, playerStatus, position, sort, statCat, statSeason, statType, statWeek]))

        #Just doing some directory setup    
        week = '%02d' % int(week)
        dirname = './raw_data/%s/%s' % (year, week)

        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except OSError:
                if os.path.exists(dirname):
                    pass
                else:
                    raise
        i = 1
        for x in urls:
            with open(('raw_data/%s/%s/player_stats_%s.html' % (year, week, i)), 'w') as f:
                headers = {
                    'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/420+ (KHTML, like Gecko) Chrome/14.0.835.186 Safari/419.3'
                    }
                    
                r = requests.get(x, headers=headers)
                f.write(r.text)

                players = self.parse_stats_nfl(f.name, year, week)
                self.upd_stats(players, year, week)
            i += 1

    def parse_stats_nfl(self, html, year, week):
        '''
        This method will parse nfl.com player stats pages. It will parse it in
        such a way that upd_player_stats() will either insert/update the info
        that is stored in the database.

        Returns Dictionary:
        {
          Player_ID:{
            PLAYER_NAME: Tony Romo,
            POS:QB,
            TEAM:DAL,
            GAME_YEAR_WEEK:{
              STATS:{
                PASS_STATS:{YDS:0, TD:0, INT:0, SACKED:0},
                RUN_STATS:{YDS:0, TD:0},
                REC_STATS:{YDS:0, TD:0},
                MISC_STATS:{RET_TD:0, FUM_TD:0, 2PT:0},
                FAN_POINTS:18.73
              }
            }
          }
        }
        
        '''
        week = '%02d' % int(week)
        
        parser = etree.HTMLParser()
        tree = etree.parse(html, parser)

        player_entries = tree.xpath('//div[@class="tableWrap"]/table[1]/tbody[1]/tr')

        players = {}
        for x in range(len(player_entries) + 1)[1:]:
            name = tree.xpath('//div[@class="tableWrap"]/table/tbody/tr[%i]/td[2]/div/a[1]' % (x))[0].text#.split('')
            (pos, team) = tree.xpath('//div[@class="tableWrap"]/table/tbody/tr[%i]/td[2]/div/em[1]' % (x))[0].text.split(' - ')
            opp = tree.xpath('//div[@class="tableWrap"]/table/tbody/tr[%i]/td[3]' % (x))[0].text.replace('@','')
            pass_yds = tree.xpath('//div[@class="tableWrap"]/table/tbody/tr[%i]/td[5]/span' % (x))[0].text.replace('-','0')
            pass_td = tree.xpath('//div[@class="tableWrap"]/table/tbody/tr[%i]/td[6]/span' % (x))[0].text.replace('-','0')
            pass_int = tree.xpath('//div[@class="tableWrap"]/table/tbody/tr[%i]/td[7]/span' % (x))[0].text.replace('-','0')
            pass_sacked = tree.xpath('//div[@class="tableWrap"]/table/tbody/tr[%i]/td[8]/span' % (x))[0].text.replace('-','0')
            rush_yds = tree.xpath('//div[@class="tableWrap"]/table/tbody/tr[%i]/td[9]/span' % (x))[0].text.replace('-','0')
            rush_td = tree.xpath('//div[@class="tableWrap"]/table/tbody/tr[%i]/td[10]/span' % (x))[0].text.replace('-','0')
            rec_yds = tree.xpath('//div[@class="tableWrap"]/table/tbody/tr[%i]/td[11]/span' % (x))[0].text.replace('-','0')
            rec_td = tree.xpath('//div[@class="tableWrap"]/table/tbody/tr[%i]/td[12]/span' % (x))[0].text.replace('-','0')
            ret_td = tree.xpath('//div[@class="tableWrap"]/table/tbody/tr[%i]/td[13]/span' % (x))[0].text.replace('-','0')
            misc_fumTD = tree.xpath('//div[@class="tableWrap"]/table/tbody/tr[%i]/td[14]/span' % (x))[0].text.replace('-','0')
            misc_2PT = tree.xpath('//div[@class="tableWrap"]/table/tbody/tr[%i]/td[15]/span' % (x))[0].text.replace('-','0')
            fum_lost = tree.xpath('//div[@class="tableWrap"]/table/tbody/tr[%i]/td[16]/span' % (x))[0].text.replace('-','0')
            fan_points = tree.xpath('//div[@class="tableWrap"]/table/tbody/tr[%i]/td[17]/span' % (x))[0].text.replace('-','0')

            players[x] = {
                'NAME': name,
                'POS': pos,
                'TEAM': team,
                'YEAR':int(year),
                'WEEK':int(week),
                'GAME': 'GAME'+ '_' + str(year) + '_' + str(week),
                'STATS':{
                    'OPP': opp,
                    'PASS_STATS':{'YDS':int(pass_yds), 'TD':int(pass_td), 'INT':int(pass_int), 'SACKED':int(pass_sacked)},
                    'RUN_STATS':{'YDS':int(rush_yds), 'TD':int(rush_td)},
                    'REC_STATS':{'YDS':int(rec_yds), 'TD':int(rec_td)},
                    'MISC_STATS':{'RET_TD':int(ret_td), 'FUM_LOST': int(fum_lost), 'FUM_TD':int(misc_fumTD), '2PT':int(misc_2PT)},
                    'FAN_POINTS': float(fan_points)
                    }
                }

        return players
    
    def upd_stats(self, players, year, week):
        '''
        args (dict(players), str(year), str(week))
        
        Takes dict of player info formatted the way parse_stats_nfl() output is
        And inserts that data into the database for use later.
        '''
        for x in players:
            team =  players[x]['TEAM']
            pos = players[x]['POS']
            name = players[x]['NAME']
            game = players[x]['GAME']
            _id = team + '_' + pos + '_' + name.replace(' ','_')

            game_info = data.db.players.find_one({'ffb_id':_id, 'GAME':game}, {'_id':1, 'ffb_id':1, 'GAME':1, 'STATS':1})
            
            if not game_info: #if player does not exist add player and game
                print('record not found creating player and game')
                data.db.players.insert({
                        'ffb_id':_id,
                        'NAME':name,
                        'POS':pos,
                        'TEAM':team,
                        'GAME':game,
                        'YEAR': int(year),
                        'WEEK': int(week),
                        'STATS': players[x]['STATS']
                        })
            elif game_info['GAME'] == game: #Player and game exist update game info (stat adjustments)
                print('record exists, updating game')
                data.db.players.update({
                        'ffb_id':_id,
                        'NAME':name,
                        'POS':pos,
                        'TEAM':team,
                        'GAME':game,
                        }, {'$set': {
                            'ffb_id':_id,
                            'NAME':name,
                            'POS':pos,
                            'TEAM':team,
                            'GAME':game,
                            'YEAR': int(year),
                            'WEEK': int(week),
                            'STATS':players[x]['STATS']}})
                
    def del_stats(self):
        raise NotImplementedError()

if __name__ == '__main__':
    year = '2012'
    weeks = ['1', '2', '3', '4', '5', '6']

    p = Players()
    for week in weeks:
        p.dl_stats_nfl(year, week)
