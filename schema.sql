CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	username TEXT,
	password TEXT
);

CREATE TABLE threads (
	id SERIAL PRIMARY KEY,
	creator_id INTEGER,
	creation_time TIMESTAMP,
	is_public BOOLEAN,
	name TEXT
);

CREATE TABLE messages (
	id SERIAL PRIMARY KEY,
	message TEXT,
	sender_id INTEGER,
	thread_id INTEGER,
	creation_time TIMESTAMP
);

CREATE TABLE thread_users (
	user_id INTEGER,
	thread_id INTEGER
);

CREATE TABLE friends (
	user_id INTEGER,
	friend_id INTEGER
);

CREATE TABLE friend_requests (
	sender_id INTEGER,
	recipient_id INTEGER
);