-- 1. User Movie Preference Analysis
SELECT user_id, user_name, genre, COUNT(*) AS watches,
       ROUND(AVG(movie_rating), 2) AS avg_rating,
       SUM(watch_time_minutes) AS total_watch_time
FROM movie_interactions
GROUP BY user_id, user_name, genre
ORDER BY user_id, watches DESC, avg_rating DESC;

-- 2 and 8. Personalized recommendation support by genre and actor affinity
SELECT movie, genre, actor, ott_platform,
       ROUND(AVG(movie_rating), 2) AS avg_rating,
       COUNT(*) AS watches,
       ROUND(AVG(watch_time_minutes), 1) AS avg_watch_time
FROM movie_interactions
GROUP BY movie, genre, actor, ott_platform
ORDER BY avg_rating DESC, watches DESC;

-- 3. Genre Popularity Analysis
SELECT genre, COUNT(*) AS watches,
       ROUND(AVG(movie_rating), 2) AS avg_rating,
       SUM(watch_time_minutes) AS total_watch_time
FROM movie_interactions
GROUP BY genre
ORDER BY watches DESC, avg_rating DESC;

-- 4. Movie Rating Analysis
SELECT movie, COUNT(*) AS watches,
       ROUND(AVG(movie_rating), 2) AS avg_rating,
       SUM(watch_time_minutes) AS total_watch_time
FROM movie_interactions
GROUP BY movie
ORDER BY avg_rating DESC, watches DESC;

-- 5. User Engagement Analysis
SELECT user_id, user_name, city, gender,
       COUNT(*) AS movies_watched,
       SUM(watch_time_minutes) AS total_watch_time,
       ROUND(AVG(watch_time_minutes), 1) AS avg_watch_time,
       ROUND(AVG(movie_rating), 2) AS avg_rating,
       MAX(watch_date) AS last_watch
FROM movie_interactions
GROUP BY user_id, user_name, city, gender
ORDER BY total_watch_time DESC, avg_rating DESC;

-- 6. Recommendation Effectiveness Analysis
SELECT COUNT(*) AS recommended_count,
       COUNT(*) FILTER (WHERE watch_history ILIKE '%' || recommended_movie || '%') AS watched_recommendation_count,
       ROUND(100.0 * COUNT(*) FILTER (WHERE watch_history ILIKE '%' || recommended_movie || '%') / COUNT(*), 2) AS watch_rate_pct,
       ROUND(AVG(movie_rating) FILTER (WHERE watch_history ILIKE '%' || recommended_movie || '%'), 2) AS avg_rating_when_watched,
       ROUND(AVG(watch_time_minutes) FILTER (WHERE watch_history ILIKE '%' || recommended_movie || '%'), 1) AS avg_watch_time_when_watched
FROM movie_interactions;

-- 7. Top Actors Popularity Analysis
SELECT actor, COUNT(*) AS watches,
       COUNT(DISTINCT movie) AS unique_movies,
       ROUND(AVG(movie_rating), 2) AS avg_rating,
       SUM(watch_time_minutes) AS total_watch_time
FROM movie_interactions
GROUP BY actor
ORDER BY watches DESC, avg_rating DESC, total_watch_time DESC;
