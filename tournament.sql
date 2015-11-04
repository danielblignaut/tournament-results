-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP VIEW IF EXISTS swiss_pairing;
DROP VIEW IF EXISTS player_list;
DROP VIEW IF EXISTS byes_view;
DROP VIEW IF EXISTS matches_view;
DROP VIEW IF EXISTS losses_view;
DROP VIEW IF EXISTS wins_view;
DROP VIEW IF EXISTS draws_view;


DROP TABLE IF EXISTS playersmatches;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS tournamentplayers;
DROP TABLE IF EXISTS tournaments;
DROP TABLE IF EXISTS players;

CREATE TABLE players (
	id BIGSERIAL PRIMARY KEY,
	name TEXT NOT NULL
);

CREATE TABLE tournaments (
	id BIGSERIAL PRIMARY KEY,
	name TEXT NOT NULL
);

CREATE TABLE tournamentplayers (
	tournamentid INTEGER REFERENCES tournaments (id) ON DELETE CASCADE,
	playerid INTEGER REFERENCES players (id) ON DELETE CASCADE
);

CREATE TABLE matches (
	id BIGSERIAL PRIMARY KEY,
	tournamentid INTEGER REFERENCES tournaments (id) ON DELETE CASCADE	
);

CREATE TABLE playersmatches (
	matchid INTEGER REFERENCES matches (id) ON DELETE CASCADE,
	playerid INTEGER REFERENCES players (id) ON DELETE CASCADE,
	outcome TEXT NOT NULL 
);

CREATE VIEW matches_view AS SELECT ROW_NUMBER() OVER (ORDER BY players.id) AS rownum,
players.id AS playerid , COUNT(playersmatches.matchid) AS matches FROM players 
LEFT OUTER JOIN playersmatches ON  playersmatches.playerid = players.id
GROUP BY players.id;

CREATE VIEW losses_view AS SELECT 
players.id AS playerid, SUM(CASE WHEN playersmatches.outcome = 'LOSS' THEN 1 ELSE 0 END)  AS losses
FROM players 
LEFT OUTER JOIN playersmatches ON  playersmatches.playerid = players.id
GROUP BY players.id;

CREATE VIEW draws_view AS SELECT 
players.id AS playerid, SUM(CASE WHEN playersmatches.outcome = 'DRAW' THEN 1 ELSE 0 END)  AS draws
FROM players 
LEFT OUTER JOIN playersmatches ON  playersmatches.playerid = players.id
GROUP BY players.id;

CREATE VIEW byes_view AS SELECT 
players.id AS playerid, SUM(CASE WHEN playersmatches.outcome = 'BYE' THEN 1 ELSE 0 END)  AS draws
FROM players 
LEFT OUTER JOIN playersmatches ON  playersmatches.playerid = players.id
GROUP BY players.id;

CREATE VIEW wins_view AS SELECT 
players.id AS playerid, players.name AS name, SUM(CASE WHEN playersmatches.outcome = 'WIN' THEN 1 ELSE 0 END)  AS wins
FROM players 
LEFT OUTER JOIN playersmatches ON  playersmatches.playerid = players.id
LEFT OUTER JOIN losses_view ON  playersmatches.playerid = losses_view.playerid
GROUP BY players.id, losses_view.losses
ORDER BY wins DESC, losses ASC;


CREATE VIEW player_list AS SELECT p1.*, ROW_NUMBER() OVER (ORDER BY p1.wins DESC) AS rownum 
FROM wins_view p1;

CREATE VIEW swiss_pairing AS SELECT p1.playerid AS player_1_id, p1.name AS player_1_name,
p2.playerid AS player_2_id, p2.name AS player_2_name 
FROM player_list p1
LEFT OUTER JOIN player_list p2 ON p1.rownum = p2.rownum + 1
WHERE  MOD(p1.rownum, 2) = 0;


