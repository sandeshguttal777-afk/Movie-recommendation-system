DROP TABLE IF EXISTS movie_interactions;

CREATE TABLE movie_interactions (
    interaction_id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    user_name TEXT NOT NULL,
    gender TEXT NOT NULL,
    city TEXT NOT NULL,
    movie TEXT NOT NULL,
    genre TEXT NOT NULL,
    actor TEXT NOT NULL,
    director TEXT NOT NULL,
    ott_platform TEXT NOT NULL,
    movie_rating NUMERIC(3, 1) NOT NULL CHECK (movie_rating BETWEEN 1 AND 5),
    watch_time_minutes INTEGER NOT NULL CHECK (watch_time_minutes >= 0),
    wishlist_movies TEXT,
    watch_history TEXT,
    recommended_movie TEXT,
    watch_date DATE NOT NULL
);

CREATE INDEX idx_movie_interactions_user_id ON movie_interactions (user_id);
CREATE INDEX idx_movie_interactions_movie ON movie_interactions (movie);
CREATE INDEX idx_movie_interactions_genre ON movie_interactions (genre);
CREATE INDEX idx_movie_interactions_actor ON movie_interactions (actor);
CREATE INDEX idx_movie_interactions_watch_date ON movie_interactions (watch_date);
