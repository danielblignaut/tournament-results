#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

tournament = 0

def setTournament (id) :
    """Sets what the current tournament is to reference it
  
    Args:
      id: the tournament id.
    """
    global tournament

    tournament = id

def registerTournament (name) : 
    """Creates a new tournament
  
    Args:
      name: the tournament name.
    """
    connection = connect()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO tournaments (name) VALUES (%s) RETURNING id', (name,) )
    connection.commit()
    id = cursor.fetchone()[0]
    connection.close()
    return id

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM matches WHERE tournamentid = " + str(tournament))
    connection.commit()
    connection.close()


def deletePlayers():
    """Remove all the player records from the database."""
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM players USING tournamentplayers " +
        "WHERE tournamentplayers.playerid = players.id ")#AND tournamentplayers.tournamentId = " + str(tournament)
    connection.commit()
    connection.close()


def countPlayers():
    """Returns the number of players currently registered."""

    connection = connect()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM players " + 
        "INNER JOIN tournamentplayers ON tournamentplayers.playerid = players.id")
    results = cursor.fetchone()[0]
    connection.close()

    return results

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player"s full name (need not be unique).
    """

    connection = connect()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO players (name) VALUES (%s) RETURNING id", (name,))
    id = cursor.fetchone()[0]
    cursor.execute("INSERT INTO tournamentplayers (playerid, tournamentid) VALUES (" +
        str(id) + ", " + str(tournament) + ")")

    connection.commit()
    connection.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player"s unique id (assigned by the database)
        name: the player"s full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    connection = connect()
    cursor = connection.cursor()
    
    cursor.execute('SELECT players.id, players.name, wins_view.wins, matches_view.matches FROM players ' +
    'LEFT OUTER JOIN matches_view ON players.id = matches_view.playerid ' +
    'LEFT OUTER JOIN wins_view ON players.id = wins_view.playerid')

    results = cursor.fetchall()

    return results

def reportMatch(winner, loser, draw = False, bye = False) :
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
      draw: a boolean stating if the match was a draw
    """
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO matches (tournamentid) VALUES (" + str(tournament) + ") RETURNING id")
    matchID = cursor.fetchone()[0]
    winnerOut = "WIN"
    loserOut = "LOSS"

    if draw :
        winnerOut = "DRAW"
        loserOut = "DRAW"

    if(bye) :
        winnerOut = "BYE"

    cursor.execute("INSERT INTO playersmatches (playerid, matchid, outcome) VALUES (%s, %s, %s)",
        (winner, matchID, winnerOut))

    if(bye == False) :
        cursor.execute("INSERT INTO playersmatches (playerid, matchid, outcome) VALUES (%s, %s, %s)",
            (loser, matchID, loserOut))

    connection.commit()
    connection.close()
 


 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player"s unique id
        name1: the first player"s name
        id2: the second player"s unique id
        name2: the second player"s name
    """

    connection = connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM swiss_pairing")
    results = cursor.fetchall()
    connection.close()

    return results;
