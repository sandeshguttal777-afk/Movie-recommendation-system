-- Run from psql after updating the CSV path if needed.
-- Example:
-- psql -U postgres -d movie_recommendations -f sql/schema.sql
-- psql -U postgres -d movie_recommendations -f sql/load_data.sql

\copy movie_interactions (
    user_id,
    user_name,
    gender,
    city,
    movie,
    genre,
    actor,
    director,
    ott_platform,
    movie_rating,
    watch_time_minutes,
    wishlist_movies,
    watch_history,
    recommended_movie,
    watch_date
) FROM 'C:\Users\Md. Tousif\Documents\Codex\2026-05-09\files-mentioned-by-the-user-movie\data\movie_recommendation_enhanced_1000.csv'
WITH (FORMAT csv, HEADER true);
