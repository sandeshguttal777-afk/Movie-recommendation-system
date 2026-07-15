from __future__ import annotations

from pathlib import Path

import pandas as pd


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "movie_recommendation_enhanced_1000.csv"


def split_titles(value: object) -> list[str]:
    if pd.isna(value):
        return []
    return [item.strip() for item in str(value).split(",") if item.strip()]


def load_movies(path: str | Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [col.strip() for col in df.columns]
    df["Watch_Date"] = pd.to_datetime(df["Watch_Date"], errors="coerce")
    df["Movie_Rating"] = pd.to_numeric(df["Movie_Rating"], errors="coerce")
    df["Watch_Time_Minutes"] = pd.to_numeric(df["Watch_Time_Minutes"], errors="coerce")
    df["Engagement_Score"] = (
        (df["Movie_Rating"].fillna(0) / 5) * 0.45
        + (df["Watch_Time_Minutes"].fillna(0) / df["Watch_Time_Minutes"].max()) * 0.55
    ).round(3)
    return df


def kpis(df: pd.DataFrame) -> dict[str, float | int]:
    return {
        "total_interactions": int(len(df)),
        "unique_users": int(df["User_ID"].nunique()),
        "unique_movies": int(df["Movie"].nunique()),
        "avg_rating": round(float(df["Movie_Rating"].mean()), 2),
        "avg_watch_time": round(float(df["Watch_Time_Minutes"].mean()), 1),
        "recommendation_watch_rate": round(float(recommendation_effectiveness(df)["watch_rate"].iloc[0]), 2),
    }


def user_preferences(df: pd.DataFrame, user_id: int | None = None) -> pd.DataFrame:
    data = df if user_id is None else df[df["User_ID"] == user_id]
    return (
        data.groupby(["User_ID", "User_Name", "Genre"], as_index=False)
        .agg(
            watches=("Movie", "count"),
            avg_rating=("Movie_Rating", "mean"),
            total_watch_time=("Watch_Time_Minutes", "sum"),
            avg_engagement=("Engagement_Score", "mean"),
        )
        .sort_values(["User_ID", "watches", "avg_rating"], ascending=[True, False, False])
    )


def genre_popularity(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Genre", as_index=False)
        .agg(
            watches=("Movie", "count"),
            avg_rating=("Movie_Rating", "mean"),
            total_watch_time=("Watch_Time_Minutes", "sum"),
            avg_engagement=("Engagement_Score", "mean"),
        )
        .sort_values(["watches", "avg_rating"], ascending=False)
    )


def movie_rating_analysis(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Movie", as_index=False)
        .agg(
            watches=("User_ID", "count"),
            avg_rating=("Movie_Rating", "mean"),
            total_watch_time=("Watch_Time_Minutes", "sum"),
            avg_engagement=("Engagement_Score", "mean"),
        )
        .sort_values(["avg_rating", "watches"], ascending=False)
    )


def user_engagement(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["User_ID", "User_Name", "City", "Gender"], as_index=False)
        .agg(
            movies_watched=("Movie", "count"),
            total_watch_time=("Watch_Time_Minutes", "sum"),
            avg_watch_time=("Watch_Time_Minutes", "mean"),
            avg_rating=("Movie_Rating", "mean"),
            avg_engagement=("Engagement_Score", "mean"),
            last_watch=("Watch_Date", "max"),
        )
        .sort_values(["total_watch_time", "avg_rating"], ascending=False)
    )


def actor_popularity(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Actor", as_index=False)
        .agg(
            watches=("Movie", "count"),
            unique_movies=("Movie", "nunique"),
            avg_rating=("Movie_Rating", "mean"),
            total_watch_time=("Watch_Time_Minutes", "sum"),
            avg_engagement=("Engagement_Score", "mean"),
        )
        .sort_values(["watches", "avg_rating", "total_watch_time"], ascending=False)
    )


def recommendation_effectiveness(df: pd.DataFrame) -> pd.DataFrame:
    watched_recommendation = df.apply(
        lambda row: row["Recommended_Movie"] in split_titles(row["Watch_History"]), axis=1
    )
    return pd.DataFrame(
        {
            "recommended_count": [int(df["Recommended_Movie"].notna().sum())],
            "watched_recommendation_count": [int(watched_recommendation.sum())],
            "watch_rate": [round(float(watched_recommendation.mean() * 100), 2)],
            "avg_rating_when_watched": [
                round(float(df.loc[watched_recommendation, "Movie_Rating"].mean()), 2)
                if watched_recommendation.any()
                else 0
            ],
            "avg_watch_time_when_watched": [
                round(float(df.loc[watched_recommendation, "Watch_Time_Minutes"].mean()), 1)
                if watched_recommendation.any()
                else 0
            ],
        }
    )


def recommend_movies(df: pd.DataFrame, user_id: int, limit: int = 10) -> pd.DataFrame:
    user_rows = df[df["User_ID"] == user_id]
    if user_rows.empty:
        return pd.DataFrame()

    watched = set(user_rows["Movie"].dropna())
    for value in user_rows["Watch_History"].dropna():
        watched.update(split_titles(value))

    wishlisted = set()
    for value in user_rows["Wishlist_Movies"].dropna():
        wishlisted.update(split_titles(value))

    preferred_genres = set(user_rows["Genre"].dropna())
    preferred_actors = set(user_rows["Actor"].dropna())
    preferred_platforms = set(user_rows["OTT_Platform"].dropna())

    catalog = (
        df.groupby(["Movie", "Genre", "Actor", "Director", "OTT_Platform"], as_index=False)
        .agg(
            avg_rating=("Movie_Rating", "mean"),
            watches=("User_ID", "count"),
            avg_watch_time=("Watch_Time_Minutes", "mean"),
            avg_engagement=("Engagement_Score", "mean"),
        )
    )
    catalog = catalog[~catalog["Movie"].isin(watched)].copy()

    if catalog.empty:
        return catalog

    max_watches = max(catalog["watches"].max(), 1)
    max_watch_time = max(catalog["avg_watch_time"].max(), 1)
    catalog["recommendation_score"] = (
        catalog["Genre"].isin(preferred_genres).astype(int) * 25
        + catalog["Actor"].isin(preferred_actors).astype(int) * 25
        + catalog["OTT_Platform"].isin(preferred_platforms).astype(int) * 10
        + catalog["Movie"].isin(wishlisted).astype(int) * 20
        + (catalog["avg_rating"] / 5) * 10
        + (catalog["watches"] / max_watches) * 5
        + (catalog["avg_watch_time"] / max_watch_time) * 5
    ).round(2)

    ranked = catalog.sort_values(
        ["recommendation_score", "avg_rating", "watches"], ascending=False
    )
    return ranked.drop_duplicates("Movie", keep="first").head(limit)


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    trend = df.dropna(subset=["Watch_Date"]).copy()
    trend["month"] = trend["Watch_Date"].dt.to_period("M").dt.to_timestamp()
    return (
        trend.groupby("month", as_index=False)
        .agg(
            watches=("Movie", "count"),
            avg_rating=("Movie_Rating", "mean"),
            total_watch_time=("Watch_Time_Minutes", "sum"),
        )
        .sort_values("month")
    )
