"""
plot.py

author: Diana Cai <caidcai@gmail.com>

queries mysql database for players from a specific team
plots info for 1v1 games/maps and 2v2 games

"""

import os
import sys
import pylab
import numpy
import model
import random

# constants
# race
ZERG = 'Z'
PROTOSS = 'P'
TERRAN = 'T'
RANDOM = 'R'

SAVEDIR = './data'

session = model.create_session()
pylab.rcParams['font.size'] = 9.0

def plot_single(teamnum):

    matches = {}
    wins = {}
    info = {}
    total_matches = 0

    # query team table to get teamname
    teamname = session.query(model.Team).filter(model.Team.cslid==teamnum).first().name
    num_players = session.query(model.Team).filter(model.Team.cslid==teamnum).first().single

    for player in session.query(model.Player).filter(model.Player.team==teamnum).all():
        if player.games > 0:
            matches[player.name] = player.games
            wins[player.name] = player.wins
            info[player.name] = (player.league, player.points, player.race)
            total_matches += player.games
            
    pylab.figure(1, figsize=(8,8))
    ax = pylab.axes([0.1, 0.1, 0.8, 0.8])
    
    labels = [] 
    fracs = []
    colors = []
    for i, key in enumerate(sorted(matches.keys())):
        percent = 100.0 * wins[key] / matches[key]
        labels.append("%s\n%s %s (%s)\n%.2f %%win" %\
                (key, info[key][0], info[key][1], info[key][2], percent))
        fracs.append(100.0 * matches[key] / total_matches)
        colors.append(pylab.cm.bone_r(i * (256 / num_players)))

    explode = [0] * len(labels)
    pylab.pie(fracs, explode=explode, \
            labels=labels, colors=colors, autopct='%1.1f%%', shadow=True)
    pylab.title('1v1 Games Played ' + teamname)
    pylab.savefig(os.path.join(SAVEDIR, str(teamnum) + '_1v1games.png'))

def plot_single_maps(teamnum):

    pylab.figure(1).clf()
    teamname = session.query(model.Team).filter(model.Team.cslid==teamnum).first().name
    num_players = session.query(model.Team).filter(model.Team.cslid==teamnum).first().single

    rowLabels =  ['Antiga', 'Daybr', 'Dual', 'Metal', 'Shakur', 'Shatter', 'Tal\'d', 'Testbug', 'Xel\'Naga'] 
    names = []
    ind = numpy.arange(len(rowLabels))
    width = 1.0 / num_players
    bars = []
    cellText = []
    i = 0
    for player in session.query(model.Player).filter(model.Player.team==teamnum).all():
        if player.games > 0:
            names.append('%s (%s)' % (player.name, player.race))
            maps = [player.antiga, player.daybreak, player.dualsight,\
                    player.metalopolis, player.shakuras, player.shattered,\
                    player.taldarim, player.testbug, player.xelnaga]

            color = pylab.cm.bone_r(i * (256 / num_players))
            bars.append(pylab.bar(ind + (i * width), maps, width, color=color))
            cellText.append(['%d' % x for x in maps])
            i += 1

    pylab.xticks(range(len(rowLabels)), rowLabels, size='small')
    pylab.yscale=('linear')
    pylab.legend(bars, names)
    pylab.grid(b=True, which='major', axis='both')

    pylab.title('Maps for 1v1 Games ' + teamname)
    pylab.xlabel('Maps')
    pylab.ylabel('Number of Times Played')

    pylab.savefig(os.path.join(SAVEDIR, str(teamnum) + '_1v1maps.png'))

def plot_teams(teamnum):

    total_matches = 0
    teamgames = {}
    info = {}
    z = {}
    p = {}
    t = {}
    r = {}
    teamname = session.query(model.Team).filter(model.Team.cslid==teamnum).first().name
    num_players = session.query(model.Team).filter(model.Team.cslid==teamnum).first().team

    for player in session.query(model.Player).filter(model.Player.team==teamnum).all():
        if player.teamgames > 0:
            teamgames[player.name] = player.teamgames
            z[player.name] = player.zteam
            p[player.name] = player.pteam
            t[player.name] = player.tteam
            r[player.name] = player.rteam
            total_matches += player.teamgames
            info[player.name] = (player.league, player.points)
                
    pylab.figure(1, figsize=(8,8)).clf()
    ax = pylab.axes([0.1, 0.1, 0.8, 0.8])
    
    labels = [] 
    fracs = []
    c = []
    for i, key in enumerate(sorted(teamgames.keys())):
        text = '%s\n %s %s\n' % (key, info[key][0], info[key][1]) 
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
        c.append(pylab.cm.bone_r(i * (256/num_players)))

    explode = [0] * len(labels)
    pylab.pie(fracs, explode=explode, \
            labels=labels, colors=c, autopct='%1.1f%%', shadow=True)
    pylab.title('2v2 Games Played ' + teamname)
    pylab.savefig(os.path.join(SAVEDIR, str(teamnum) + '_2v2games.png'))

if __name__=='__main__':
    teamnum = sys.argv[1]

    plot_single(teamnum)
    plot_single_maps(teamnum)
    plot_teams(teamnum)
    plot_ace(teamnum)

