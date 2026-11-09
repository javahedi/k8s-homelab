CREATE TABLE IF NOT EXISTS jobs (
    id integer PRIMARY KEY,
    title text NOT NULL,
    city text NOT NULL
);

INSERT INTO jobs (id, title, city)
VALUES
    (1, 'Python Developer', 'Berlin'),
    (2, 'Kubernetes Administrator', 'Bremen')
ON CONFLICT (id) DO NOTHING;
