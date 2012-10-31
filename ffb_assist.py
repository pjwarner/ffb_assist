import conn as data
from StringIO import StringIO
from team_data.ffb_team import nfl

#Get all players against OPP at POS gt 0.01
def get_player_info(ffb_id):
    result = data.db.players.find_one({"ffb_id":ffb_id})
    return result

def get_opp(team, year, week):
    result = data.db.nfl_sch.find_one({"YEAR":year, "WEEK":week, "TEAM":team}, {"_id":0, "OPP":1})
    if result:
        return result['OPP']
    else:
        return "Bye"

def get_opp_points_against(opp, pos):
    if opp != 'Bye':
        stats = data.db.players.find({"STATS.FAN_POINTS":{"$gt":0.01}, "POS":pos, "STATS.OPP":opp}, {"_id":0, "STATS.FAN_POINTS":1})
        
        count = 0
        total_fan_points = 0
        avg_fan_points = 0
        
        for stat in stats:
            total_fan_points += stat['STATS']['FAN_POINTS']
            count += 1

            avg_fan_points = total_fan_points / count
        return (total_fan_points, avg_fan_points)
    else:
        return 0, 0

def player_research(ffb_id, year=2012, week=8):
    p_info = get_player_info(ffb_id)
    opp = get_opp(p_info['TEAM'], year, week)
    total, avg = get_opp_points_against(opp, p_info['POS'])

    if total != 'Bye':
        name = ' [' + p_info['POS'] + '] ', p_info['NAME'], ' vs ' + opp + ':'
        total = '\tTotal:\t', '%.2f' % total
        avg = '\tAvg:\t', '%.2f' % avg

        return (name, total, avg)
    else:
        return(name, 'Bye', 'Bye')
    
if __name__ == '__main__':
    '''
    NYG_QB_Eli_Manning
    HOU_RB_Arian_Foster
    SF_RB_Frank_Gore
    MIN_WR_Percy_Harvin
    CIN_WR_A.J._Green
    MIN_TE_Kyle_Rudolph
    GB_WR_James_Jones
    TB_WR_Mike_Williams
    PHI_RB_LeSean_McCoy
    HOU_RB_Ben_Tate
    NE_RB_Danny_Woodhead
    KC_WR_Dwayne_Bowe
    NO_TE_Jimmy_Graham
    '''
    team = nfl()
    while True:
        update = raw_input('Would you like to update your team?[Y/n] ')
        if not update or (update == 'Y') or (update == 'y'):
            html = team.get_players(592090, 3, False)
            with open('raw_data/ffb_team.html', 'w') as f:
                f.write(html.getvalue())

        with open('raw_data/ffb_team.html', 'r') as f:
            players = team.parse_players(f)
            for x in players: print players[x]["_id"]
            break
    
    # players = ['NO_TE_Jimmy_Graham', 'GB_WR_James_Jones', 'MIN_TE_Kyle_Rudolph', 'NE_RB_Danny_Woodhead']
    for x in players:
        result = player_research(players[x]["_id"])
        print ''.join(result[0])
        print ''.join(result[1])
        print ''.join(result[2])
