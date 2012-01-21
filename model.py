from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

SERVER = 'localhost'
DB = 'csl'
USER = 'root'
PW = ''

def create_session(server=SERVER, db=DB, user=USER, pw=PW):

    engine = create_engine("mysql://%s:%s@%s/%s" \
            % (user, pw, server, db))
    # creates tables if necessary
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

class Player(Base):

    __tablename__ = 'player'

    id = Column(Integer, primary_key=True)
    cslid = Column(Integer)

    # character.123
    name = Column(String(50))
    character = Column(String(50))
    code = Column(Integer)
    # csl id for team
    team = Column(Integer)

    # main race listed on CSL
    race = Column(String(10))
    league = Column(String(10))
    points = Column(Integer)
    
    # total 1v1 games played
    games = Column(Integer)
    # games played against z, p, t
    zgames = Column(Integer)
    pgames = Column(Integer)
    tgames = Column(Integer)
    # total wins
    wins = Column(Integer)
    # against zerg
    zwins = Column(Integer)
    # against protoss
    pwins = Column(Integer)
    # against terran
    twins = Column(Integer)

    # number of times played on map
    antiga = Column(Integer)
    daybreak = Column(Integer)
    dualsight = Column(Integer)
    metalopolis = Column(Integer)
    shakuras = Column(Integer)
    shattered = Column(Integer)
    taldarim = Column(Integer) # added
    testbug = Column(Integer) # taken out
    xelnaga = Column(Integer)
    
    # number of ace games played 
    ace = Column(Integer) 

    # number of team games played
    teamgames = Column(Integer)
    # number of team wins
    teamwins = Column(Integer)
    # number of team games as z, p, t, r
    zteam = Column(Integer)
    pteam = Column(Integer)
    tteam = Column(Integer)
    rteam = Column(Integer) #??

    #time = Column(String(50)) # timestamp?

class Team(Base):

    __tablename__ = 'team'

    id = Column(Integer, primary_key=True)

    # csl team id
    cslid = Column(Integer)
    # team name
    name = Column(String(50))
    
    # number of active players on the team
    active_players = Column(Integer)
    # number of active 1v1 players
    single = Column(Integer)
    # number of active 2v2 players
    team = Column(Integer)

    # number of zerg, protoss, terran
    zerg = Column(Integer)
    protoss = Column(Integer)
    terran = Column(Integer)
    random = Column(Integer)

    #time = Column(String(50)) 

