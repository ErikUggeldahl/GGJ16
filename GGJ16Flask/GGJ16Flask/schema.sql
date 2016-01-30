drop table if exists players;
drop table if exists games;
drop table if exists rituals;
drop table if exists ritual_players;

create table players (
  id integer primary key autoincrement,
  name text not null
);

create table games (
  id integer primary key autoincrement,
  name text not null
);

create table rituals (
  id integer primary key autoincrement,
  game_id integer not null,
  leader_id integer not null,
  name text not null,
  foreign key(game_id) references games(id)
  foreign key(leader_id) references players(id)
);

create table ritual_players (
  id integer primary key autoincrement,
  game_id integer not null,
  ritual_id integer not null,
  player_id integer not null,
  foreign key(game_id) references games(id),
  foreign key(ritual_id) references rituals(id),
  foreign key(player_id) references players(id)
);

insert into games values (null, 'Test Game');
insert into players values (null, 'Ritual Leader!');
insert into players values (null, 'Other ritual leader!');
insert into players values (null, 'Test Player!');
insert into players values (null, 'Test Player 2');
insert into rituals values (null, 1, 1, 'My Ritual');
insert into rituals values (null, 1, 2, 'My Other Ritual');
insert into ritual_players values (null, 1, 1, 2);
insert into ritual_players values (null, 1, 1, 3);