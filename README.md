#Tournament Results Manager

All extra requirements were met purely through SQL manipulation through the use of views, aggregator functions and table joins.

##Change to Structure

In order to support multiple tournaments, a tournament table was introduced that could keep track of this. Thus, the tournament test file was manipulated to first generate a tournament and secoondly set a global tournament variable for the current active tournament (to avoid having to change the parameters of all methods to have to accept a tournament parameter)

The report match function was also manipulated. Two parameters were added to it, the first to check if the match was a draw and the second to check if the match generated was created to keep track of a player's bye match.

##Getting Started

In order to get started:

1. run the psql command to open the PostgreSQL command line tool
2. run \i tournament.sql to set up the database, tables & appropriate views
3. run \q to return to your terminal
4. run python tournament_test.py to execute the test program.