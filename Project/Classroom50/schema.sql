DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS classrooms;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS assignments;
DROP TABLE IF EXISTS submissions;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE INDEX index_users ON users (id, name, password, role);

CREATE TABLE classrooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    owner_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    subject TEXT,
    code TEXT UNIQUE NOT NULL,
    FOREIGN KEY(owner_id) REFERENCES users(id)
);

CREATE INDEX index_classrooms ON classrooms (id, owner_id, name, description, subject);

CREATE TABLE members (
    classroom_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(classroom_id) REFERENCES classrooms(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE INDEX index_members ON members (classroom_id, user_id);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    classroom_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    FOREIGN KEY(classroom_id) REFERENCES classrooms(id),
    FOREIGN KEY(author_id) REFERENCES users(id)
);

CREATE INDEX index_posts ON posts (id, classroom_id, author_id, timestamp, title, body);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    classroom_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    body TEXT NOT NULL,
    FOREIGN KEY(classroom_id) REFERENCES classrooms(id),
    FOREIGN KEY(post_id) REFERENCES posts(id),
    FOREIGN KEY(author_id) REFERENCES users(id)
);

CREATE INDEX index_comments ON comments (id, classroom_id, post_id, author_id, timestamp, body);

CREATE TABLE assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    classroom_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    deadline DATETIME,
    FOREIGN KEY(classroom_id) REFERENCES classrooms(id),
    FOREIGN KEY(author_id) REFERENCES users(id)
);

CREATE INDEX index_assignments ON assignments (id, classroom_id, author_id, timestamp, title, deadline);

CREATE TABLE submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    classroom_id INTEGER NOT NULL,
    assignment_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    folder_path TEXT NOT NULL,
    grade INTEGER,
    FOREIGN KEY(classroom_id) REFERENCES classrooms(id),
    FOREIGN KEY(assignment_id) REFERENCES assignments(id),
    FOREIGN KEY(author_id) REFERENCES users(id)
);

CREATE INDEX index_submissions ON submissions (id, classroom_id, assignment_id, author_id, filename, folder_path, grade);