#!/usr/bin/env python

class player_test():
    def test(self):
        from player_data.players import Players
        p = Players()
        print p

class team_test():
    def test(self):
        from team_data.ffb_team import test
        t = test()
        a = t.dev()
        for x in a: print a[x]['NAME']

#        rows = [a[1]['NAME'], a[2]['NAME'], a[3]['NAME']]
#        test = '|'.join(rows)
#        print test
        
