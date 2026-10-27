PRAGMA foreign_keys = ON;

CREATE TABLE namespaces (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    namespace_id INTEGER NOT NULL,
    FOREIGN KEY (namespace_id) REFERENCES namespaces(id) ON DELETE RESTRICT
);
