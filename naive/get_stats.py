import os
import sys
import player
import pylab
import numpy

# constants
# race
ZERG = 'Z'
PROTOSS = 'P'
TERRAN = 'T'
RANDOM = 'R'

SAVEDIR = './data'

"""
get_players(): grabs and parses the html, returns a list of player objects

arguments:
    * team_num: CSL team number
    * maps: list of maps to compare against

returns:
    list of player objects?

"""
def get_players(team_num, maps):

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
        
        #playa.print_values()    
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


    #for p in players:
    #    p.print_values()
    #    print ""

    return players, teamname

def get_colors():
    ca = [0.6, 0.8, 0.6, 0.4]
    cb = [0.3, 0.6, 0.6]
    cc = [0.3, 0.6, 0.9]
    cd = [0.2, 0.2, 0.4]
    ce = [0.7, 0.3, 0.4]
    cf = [0.5, 0.1, 0.3]
    cg = [0.0, 0.2, 0.3]
    colors = [ca, ce, cc, cd, cb, cf, cg, 'b', 'g', 'c', 'm', 'r', 'y', 'w']
    return colors

def plot_single(players, teamnum, teamname):
    total_matches = 0
    matches = {} # matches[player] = number of 1v1 games played
    info = {}
    wins = {}
    for player in players:
        if player.match:
            matches[player.character] = 0
            wins[player.character] = 0
            info[player.character] = (player.league, player.points, player.race)
            for match in player.match.keys():
                total_matches += 1
                matches[player.character] += 1
                if player.match[match][1]:
                    wins[player.character] += 1
            
    pylab.figure(1, figsize=(8,8))
    ax = pylab.axes([0.1, 0.1, 0.8, 0.8])
    
    labels = [] #sorted(matches.keys())
    fracs = []
    for key in sorted(matches.keys()):
        labels.append(key + '\n' + info[key][0] + ' ' + info[key][1] + ' (' + info[key][2] + ')\n' \
                + str(100 * wins[key]/ matches[key]) + '% win')
        fracs.append(100.0 * matches[key] / total_matches)
    #print str(labels)
    #print str(fracs)
    #print str(matches)

    explode = [0] * len(labels)
    colors = get_colors()
    pylab.pie(fracs, explode=explode, \
            labels=labels, colors=colors, autopct='%1.1f%%', shadow=True)
    pylab.title('1v1 Games Played ' + teamname)
    pylab.savefig(os.path.join(SAVEDIR, str(teamnum) + '_1v1games.png'))

def plot_single_maps(players, teamnum, teamname):

    c = get_colors()
    pylab.figure(1).clf()
    map_pool = ['Antiga', 'Testbug', 'Dual', 'Metalopolis', 'XelNaga',\
            'Shakuras', 'Daybreak', 'Shattered']

    num_players = 0
    for player in players:
        if player.maps:
            num_players += 1

    data = [] 
    for player in range(0, num_players):
        mappas = []
        for i in range(0, len(map_pool)):
            mappas.append(0)
        data.append(mappas)

    i = 0
    p = []
    for player in players:
        if player.maps:
            p.append(player.character)
            maps = []
            for key in sorted(player.maps.keys()):
                for m in map_pool:
                    if m in key:
                        map_index = map_pool.index(m)
                data[i][map_index] = int(player.maps[key])
            i += 1

    #ind = [0, 1, 2, 3, 4, 5, 6, 7]
    ind = numpy.arange(len(map_pool))
    width = 1.0/num_players

    bars = []
    cellText = []
    for player in range(0, num_players):
        bars.append(pylab.bar(ind+(player*width), data[player], width, color=c[player]))
        cellText.append(['%d' % x for x in data[player]])

    #for i in range(0, len(map_pool)):
    #    pylab.xticks(i, map_pool[i])
    rowLabels =  ['Antiga', 'Testbug', 'Dual', 'Meta', 'XNC', 'Shakur', 'Dayb', 'Shattered'] 
    pylab.xticks(range(8), rowLabels, size='small')
    pylab.yscale=('linear')

    pylab.legend(bars, p)
    
    pylab.grid(b=True, which='major', axis='both')

    pylab.title('Maps for 1v1 Games ' + teamname)
    pylab.xlabel('Maps')
    pylab.ylabel('Number of Times Played')

    pylab.savefig(os.path.join(SAVEDIR, str(teamnum) + '_1v1maps.png'))
    
    #pylab.figure(1).clf()
    
    cellText.reverse()
    c.reverse()
    table = pylab.table(cellText=cellText, rowLabels=p, colLabels=rowLabels)
    pylab.savefig(os.path.join(SAVEDIR, str(teamnum) + '_1v1maps_table.pdf'))

def plot_teams(players, teamnum, teamname):
    total_matches = 0
    teamgames = {}
    info = {}
    z = {}
    p = {}
    t = {}
    r = {}
    for player in players:
        if player.teamgame:
            teamgames[player.character] = 0
            z[player.character] = 0
            p[player.character] = 0
            t[player.character] = 0
            r[player.character] = 0
            info[player.character] = (player.league, player.points)
            for game in player.teamgame.keys():
                total_matches += 1
                teamgames[player.character] += 1
                if ZERG in player.teamgame[game][0][0]:
                    z[player.character] += 1
                elif PROTOSS in player.teamgame[game][0][0]:
                    p[player.character] += 1
                elif TERRAN in player.teamgame[game][0][0]:
                    t[player.character] += 1
                else:
                    r[player.character] += 1

    pylab.figure(1, figsize=(8,8)).clf()
    ax = pylab.axes([0.1, 0.1, 0.8, 0.8])
    
    labels = [] #sorted(matches.keys())
    fracs = []
    for key in sorted(teamgames.keys()):
        text = key + '\n(' + info[key][0] + ' ' + info[key][1] + ')\n'
        if z[key]:
            text += 'Z:' + str(z[key]) + ' ' 
        if p[key]: 
            text += 'P: ' + str(p[key]) + ' '
        if t[key]:
            text += 'T: ' + str(t[key]) + ' '
        if r[key]:
            text += 'R: ' + str(r[key])
        labels.append(text)
        fracs.append(100.0 * teamgames[key] / total_matches)
    explode = [0] * len(labels)
    colors = get_colors()
    pylab.pie(fracs, explode=explode, \
            labels=labels, colors=colors, autopct='%1.1f%%', shadow=True)
    pylab.title('2v2 Games Played ' + teamname)
    pylab.savefig(os.path.join(SAVEDIR, str(teamnum) + '_2v2games.png'))





if __name__=='__main__':
    teamnum = sys.argv[1]
    players, teamname = get_players(teamnum, [])
    #49 dalhousie, 182 harvard
    plot_single(players, teamnum, teamname)
    plot_single_maps(players, teamnum, teamname)
    plot_teams(players, teamnum, teamname)
