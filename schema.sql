CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    content TEXT NOT NULL CHECK (length(content) BETWEEN 1 AND 1000),
    sentiment TEXT NOT NULL CHECK (sentiment IN ('positive', 'negative', 'neutral')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE
);

INSERT OR IGNORE INTO courses (id, name) VALUES
    (1, 'Inteligencia Artificial'),
    (2, 'Sistemas Operativos'),
    (3, 'Compiladores e Intérpretes'),
    (4, 'Bases de Datos I'),
    (5, 'Bases de Datos II'),
    (6, 'Diseño de Software'),
    (7, 'Administración de Proyectos'),
    (8, 'Requerimientos de Software'),
    (9, 'Computación y Sociedad');
