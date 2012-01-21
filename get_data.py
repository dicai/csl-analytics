"""
get_data.py

grabs html from /stats/team/ (these are a list of valid team rankings)
parses and gets info from it.

Author: Diana Cai <caidcai@gmail.com>

01/21/12: currently just gets a list of the valid schools for the scraper
"""
import sys
import os

def get_all_schools():
    """
    scrapes the webpage with the list of valid school rankings 
        (so filters out suspended schools, etc)
    args:
        none
    returns:
        a set of unique school ids participating in current season of CSL
    """

    os.system('curl -# "http://www.cstarleague.com/stats/team" > out')
    os.system('grep "/league/teams/" out > parse')
    
    f = open('parse', 'r')
    ids = set()
    for line in f:
        ids.add(int(line.split('href="')[1].split('"')[0].split('/')[3]))

    os.system('rm out | rm parse')

    return ids

def get_all_data(drop=True):

    if drop:
        # drop tables in csl table
        import model
        model.drop_all()

    ids = get_all_schools()

    for id in ids:
        print id
        sys.stdout.flush()
        os.system('python scrape.py %d' % id)


if __name__=="__main__":
    get_all_data()
