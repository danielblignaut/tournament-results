#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import contextlib

tournament = 0

def setTournament (id) :
    """Sets what the current tournament is to reference it
  
    Args:
      id: the tournament id.
    """
    global tournament

    tournament = id

@contextlib.contextmanager
def get_cursor():
    """
    This function is responsible for returning a cursor instance 
    by using the context manager and the above decorator
    """
    conn = connect()
    cur = conn.cursor()
    try:
        yield cur
    except:
        raise
    else:
        conn.commit()
    finally:
        cur.close()
        conn.close()

def registerTournament (name) : 
    """Creates a new tournament that players can be registered to as welll as matches
  
    Args:
      name: the tournament name.
    """
    with get_cursor() as cursor:
        cursor.execute('INSERT INTO tournaments (name) VALUES (%s) RETURNING id', (name,) )
        id = cursor.fetchone()[0]

    return id

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""

    """Removes all matches linked to the active tournament"""

    with get_cursor() as cursor:
        cursor.execute("DELETE FROM matches WHERE tournamentid = %s", (tournament,))



def deletePlayers():
    """Remove all the player records from the database."""
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM players USING tournamentplayers " +
            "WHERE tournamentplayers.playerid = players.id AND " +
            "tournamentplayers.tournamentId = %s", (tournament,))
    

def countPlayers():
    """Returns the number of players currently registered."""

    """It Counts all players registered within the current tournament"""

    with get_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM players " + 
            "INNER JOIN tournamentplayers ON tournamentplayers.playerid = players.id" +
            "WHERE tournamentplayers.tournamentid = %s", (tournament))
        results = cursor.fetchone()[0]

    return results

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player"s full name (need not be unique).
    """

    """Inserts a player into the database and links the player 
    inserted to the active tournament"""

    with get_cursor() as cursor:
        cursor.execute("INSERT INTO players (name) VALUES (%s) RETURNING id", (name,))
        id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO tournamentplayers (playerid, tournamentid) VALUES (%s, %s)", (id, tournament))

    


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

    """To get the current match standings, it makes use of the wins view as 
    well as the matches view. These views hold total wins for all players 
    and matches using the SUM function with a case so that they
    default to zero and not undefined if there are no wins or matches 
    for a given player. These views are joined via the player ID"""

    with get_cursor() as cursor:
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

    """By adding the draw and bye function, it can create a record 
    for a given user (a relationship between the match table and 
    user table) that keeps track of the win, loss, draw or bye for 
    the given player. If the user receives a bye, they must be the winner parameter.
    Firstly, a match is generated linked to the tournament. The results for the players
    are then inserted into the playersmatches relational table"""

    with get_cursor() as cursor:
        cursor.execute("INSERT INTO matches (tournamentid) " +
            "VALUES (%s) RETURNING id", (tournament,))
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

    """The swiss pairings view makes use of the wins view which holds are players id & their wins.
    It is ordered by wins descending and secondly by loses ascending by making use of a join on the
    losses (stores all player ID's and their losses) on the player ID. the players list view queries
    the wins view and adds new row numbers so that the swiss pairings table can select every second row
    by using the mod operator on the generated row ID. Row ID has to be generated as player ID is not
    in orrder as the table is ordered by wins. This view joins the playerlist view to itself on the players
    id = the players id + 1 so that alternating players are matched. A left outer join means that it can
    handle an odd number of players."""

    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM swiss_pairing")
        results = cursor.fetchall()
    
    return results;
