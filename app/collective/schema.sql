-- schema.sql

CREATE TABLE persons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    bio VARCHAR(500),
    location VARCHAR(100)
);

CREATE TABLE collectives (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    location VARCHAR(100)
);

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500)
);

CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500)
);

CREATE TABLE belongs_to (
    person_id INT REFERENCES persons(id),
    collective_id INT REFERENCES collectives(id),
    PRIMARY KEY (person_id, collective_id)
);

CREATE TABLE possesses (
    person_id INT REFERENCES persons(id),
    skill_id INT REFERENCES skills(id),
    PRIMARY KEY (person_id, skill_id)
);

CREATE TABLE participates (
    person_id INT REFERENCES persons(id),
    project_id INT REFERENCES projects(id),
    PRIMARY KEY (person_id, project_id)
);

CREATE TABLE organizes (
    collective_id INT REFERENCES collectives(id),
    project_id INT REFERENCES projects(id),
    PRIMARY KEY (collective_id, project_id)
);

CREATE TABLE requires (
    project_id INT REFERENCES projects(id),
    skill_id INT REFERENCES skills(id),
    PRIMARY KEY (project_id, skill_id)
);
