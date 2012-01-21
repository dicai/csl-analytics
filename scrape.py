"""
scrape.py

Scrapes the CSL website for player and team information,
inserting that information into a database.

author: Diana Cai
update: 01/12/12- store player/team info into mysql db

sample usage:
    python scrape.py 182

TODO:
    use BeautifulSoup or other html parser
    get rid of intermediate step 

"""
import os
import sys
import player
import model

# constants
# race
ZERG = 'Z'
PROTOSS = 'P'
TERRAN = 'T'
RANDOM = 'R'

SAVEDIR = './data'

session = model.create_session()

def get_players(team_num):

    """
    get_players(): grabs and parses the html, returns a list of player objects

    arguments:
        * team_num: CSL team number
        * maps: list of maps to compare against

    returns:
        list of player objects

    """

    players = [] # list to return 

    link = 'www.cstarleague.com/league/teams/' + str(team_num)
    os.system('curl -# %s >> mainpage.html' % link)
    #os.system('grep "/league/matches" mainpage.html > match')   
    os.system('grep "/league/players" mainpage.html > player')   
    os.system('grep "<title>" mainpage.html > team')   

    os.system('rm mainpage.html')
    
    file = open('player', 'r')
    # iterate through players, collect stats from ones who've played
    for line in file:
        if 'contact' in line:
            continue
        link = 'www.cstarleague.com' + line.split('"')[1] 
        os.system('curl -# %s > player.html' % link)
        os.system('grep "Match History" player.html > info')

        f = open('info', 'r')
        use_player = False
        match_history = f.readline()
        if "Match History" in match_history:
            use_player = True
        f.close()
        os.system('rm info')

        # ignore if no match history
        if use_player is False:
            continue

        # create player object
        playa = player.Player() # cuz sc2 kids are pimps lol
        CSLid = line.split('"')[1].split('/')[3]
        playa.add_id(CSLid)

        use_line = False
        single = False
        double = False
        ace = False
        win = False
        teamwin = False
        matchid = 0
        double_count = 0
        field = ''
        m = ''
        race1 = ''
        race2 = ''
        part = ''

        playerhtml = open('player.html', 'r')
        for pline in playerhtml:
            if '<div class="profile-row-title">Character</div>' in pline:
                field = 'character'
                use_line = True
            if '<div class="profile-row-title">Main Race</div>' in pline:
                field = 'race'
                use_line = True
            if '<div class="module-row-title small gold">vs T' in pline:
                field = 'Terran'
                use_line = True
            if '<div class="module-row-title small gold">vs P' in pline:
                field = 'Protoss'
                use_line = True
            if '<div class="module-row-title small gold">vs Z' in pline:
                field = 'Zerg'
                use_line = True
            if '<div class="module-row-title small">League' in pline:
                field = 'league'
                use_line = True
            if '<div class="module-row-title small">Points' in pline:
                field = 'points'
                use_line = True
            if '1vs1 Matches</th>' in pline:
                single = True
                double = False
            if '2vs2 Matches</th>' in pline:
                double = True
                single = False
            if '"font-weight: bold;" href="/league/players/' in pline:
                if '/league/players/' + CSLid in pline:
                    win = True
                else:
                    win = False
            #if '/league/players/' in pline and CSLid not in pline:
            #    opponent = 
            if '<div><a href="/league/matches/' in pline:
                field = 'match'
                ace = False
                prev = matchid 
                matchid = pline.split('/')[3].split('"')[0]
                if matchid == prev:
                    ace = True
                use_line = True
            if double is True:
                if '<img src="/images/icons/tick.png"' in pline:
                    if double_count % 4 is 0:
                        teamwin = True
                    else:
                        teamwin = False
                if '/league/players/' in pline:
                    double_count += 1
                    #print 'DOUBLE COUNT: ' + str(double_count)
                    #print str(double_count % 4)
                    if CSLid in pline:
                        field = 'double player'
                        use_line = True
                    if CSLid not in pline:
                        if double_count % 4 > 0 and double_count % 4 <= 2:
                            field = 'double partner'
                            use_line = True
                if '<div style="color: grey;' in pline:
                    if double_count % 4 is 2:
                        field = 'double partner'
                        use_line = True

            if use_line is True:
                if field is 'character' and 'profile-row-value' in pline: 
                    character = pline.split('>')[1].split('<')[0]
                    playa.add_character(character)
                    use_line = False
                if field is 'race' and 'profile-row-value' in pline:
                    if 'Zerg' in pline:
                        playa.add_race(ZERG)
                    elif 'Protoss' in pline:
                        playa.add_race(PROTOSS)
                    elif 'Terran' in pline: 
                        playa.add_race(TERRAN)
                    else:
                        playa.add_race(RANDOM)
                    use_line = False
                if field is 'Terran' and 'module-row-text small' in pline:
                    text = pline.split('>')[1].split('<')[0]
                    record = (text.split()[0], text.split()[2])
                    playa.add_record(TERRAN, record)
                    use_line = False
                if field is 'Protoss' and 'module-row-text small' in pline:
                    text = pline.split('>')[1].split('<')[0]
                    record = (text.split()[0], text.split()[2])
                    playa.add_record(PROTOSS, record)
                    use_line = False
                if field is 'Zerg' and 'module-row-text small' in pline:
                    text = pline.split('>')[1].split('<')[0]
                    record = (text.split()[0], text.split()[2])
                    playa.add_record(ZERG, record)
                    use_line = False

                if field is 'league' and ' </div>' in pline:
                    league = pline.split()[0]
                    if 'div' in league:
                        playa.add_league('not found')
                    else:
                        playa.add_league(league)
                    use_line = False
                if field is 'points' and ' </div>' in pline:
                    pts = pline.split()[0]
                    if 'div' in pts:
                        playa.add_points('not found')
                    else:
                        playa.add_points(pts)
                    use_line = False
                if field is 'match' and '<div style="col' in pline:
                    if single is True:
                        match_map = pline.split('>')[1].split('<')[0]
                        if ace is True:
                            playa.add_ace()
                            matchid += 'A'
                        playa.add_match(matchid, 'foo', match_map, win) 
                        playa.add_map(match_map)
                        if win is True:
                            playa.add_win(match_map)
                    if double is True:
                        match_map = pline.split('>')[1].split('<')[0]
                        playa.add_teammap(part, match_map, teamwin)
                    use_line = False
                if 'double' in field:
                    r = ''
                    if '/images/icons/sc2' in pline:
                        race = pline.split('_')[1].split('.')[0]
                        if 'zerg' in race:
                            r = ZERG
                        elif 'protoss' in race:
                            r = PROTOSS
                        elif 'terran' in race:
                            r = TERRAN
                        else:
                            r = RANDOM
                    if 'player' in field and '/icons/sc2' in pline:
                        race1 = r
                        playa.add_teamgame_race(race1)
                        use_line = False
                    if 'partner' in field:
                        if '/icons/sc2' in pline:
                            race2 = r
                            use_line = False
                    if '<div style="color: grey;' in pline:
                        if double_count % 4 is 2:
                            if playa.character not in pline:
                                part = pline.split('>')[1].split('<')[0]
                                playa.add_teamgame(part, race1, race2, '', '')
                                use_line = False
        
        players.append(playa)

    file.close()
    playerhtml.close()
    os.system('rm player')
    os.system('rm player.html')

    f = open('team', 'r')
    fread = f.readline()
    teamname = fread.split('>')[1].split(' |')[0]
    f.close()
    os.system('rm team')

    return players, teamname

def insert_players(players, teamnum, teamname):
    # lazy so doing this intermediate step for now
    """ 
    Takes the player objects and puts info into mysql db 
    
    args:
    * players: list of player objects
    * teamnum: CSL id for team, e.g. 182
    * teamname: string for teamname, e.g. 'Harvard University'

    returns:
        nothing
    """

    active = len(players)
    singleplayers = 0
    teamplayers = 0
    zerg = 0
    protoss = 0
    terran = 0
    random = 0

    for player in players:

        games = len(player.match.keys())

        ztotal = 0
        ptotal = 0
        ttotal = 0
        zwins = 0
        pwins = 0
        twins = 0
        wins = 0
        plays = [0] * 9

        if games is not 0:
            zgames = player.record[ZERG]
            pgames = player.record[PROTOSS]
            tgames = player.record[TERRAN]

            ztotal = int(zgames[0]) + int(zgames[1])
            ptotal = int(pgames[0]) + int(pgames[1]) 
            ttotal = int(tgames[0]) + int(tgames[1])

            try:
                # this doesn't work as an equality because CSL website doesn't
                # account for random players in their record
                assert int(games) >= int(ztotal + ptotal + ttotal)
            except:
                print player.character
                sys.stdout.flush()

            zwins = int(zgames[0])
            pwins = int(pgames[0])
            twins = int(tgames[0])

            wins = zwins + pwins + twins

            maps = ['Antiga', 'Daybreak', 'Dual', 'Metal', 'Shakuras',\
                    'Shattered', 'Tal', 'Testbug', 'XelNaga']
            plays = [0] * len(maps)

            for m in player.maps.keys():
                for mm in maps:
                    if mm in m:
                        plays[maps.index(mm)] = player.maps[m]

        teamgames = 0
        teamwins = -1 # TODO: not implemented yet
        team = [0] * 4
        for race in player.teamgame_race.keys(): 
            teamgames += player.teamgame_race[race]
            #teamwins += player.teamwins_race[race] # not implemented yet
            if ZERG in race:
                team[0] = player.teamgame_race[race]
            elif PROTOSS in race:
                team[1] = player.teamgame_race[race]
            elif TERRAN in race:
                team[2] = player.teamgame_race[race]
            else:
                team[3] = player.teamgame_race[race]

        assert teamgames == (team[0] + team[1] + team[2] + team[3])
        assert teamwins <= teamgames
  
        # to get case of 'not found' for player's points
        try:
            pts = int(player.points)
        except:
            pts = -1

        session.add(model.Player(cslid=player.CSLid,\
                            name=player.character,\
                            character=player.character.split('.')[0],\
                            code=player.character.split('.')[1],\
                            team=teamnum,\
                            race=player.race,\
                            league=player.league,\
                            points=pts,\
                            games=games,\
                            zgames=ztotal,\
                            pgames=ptotal,\
                            tgames=ttotal,\
                            wins=wins,\
                            zwins=zwins,\
                            pwins=pwins,\
                            twins=twins,\
                            antiga=plays[0],\
                            daybreak=plays[1],\
                            dualsight=plays[2],\
                            metalopolis=plays[3],\
                            shakuras=plays[4],\
                            shattered=plays[5],\
                            taldarim=plays[6],\
                            testbug=plays[7],\
                            xelnaga=plays[8],\
                            ace=player.ace,\
                            teamgames=teamgames,\
                            teamwins=teamwins,\
                            zteam=team[0],\
                            pteam=team[1],\
                            tteam=team[2],\
                            rteam=team[3]))

        session.commit()

        if player.match:
            singleplayers += 1
        if player.teamgame:
            teamplayers += 1
            
        if player.race is ZERG:
            zerg += 1
        elif player.race is PROTOSS:
            protoss += 1
        elif player.race is TERRAN:
            terran += 1
        else:
            random += 1
            

    session.add(model.Team(cslid=teamnum,\
                    name=teamname,\
                    active_players=len(players),\
                    single=singleplayers,\
                    team=teamplayers,\
                    zerg=zerg,\
                    protoss=protoss,\
                    terran=terran,\
                    random=random))

    session.commit()

    session.close()


if __name__=='__main__':
    teamnum = sys.argv[1]
    players, teamname = get_players(teamnum)

    insert_players(players, teamnum, teamname)
