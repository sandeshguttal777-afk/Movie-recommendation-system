from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from src.analytics import (
    DATA_PATH,
    actor_popularity,
    genre_popularity,
    load_movies,
    monthly_trend,
    movie_rating_analysis,
    recommendation_effectiveness,
    user_engagement,
)


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "report_visualizations"


def save_plot(fig: plt.Figure, filename: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, dpi=180, bbox_inches="tight")
    plt.close(fig)


def add_labels(ax, orient: str = "vertical") -> None:
    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="%.0f",
            padding=3,
            fontsize=9,
            label_type="edge",
        )
    if orient == "vertical":
        ax.margins(y=0.12)
    else:
        ax.margins(x=0.12)


def main() -> None:
    sns.set_theme(style="whitegrid", palette="Set2")
    df = load_movies(DATA_PATH)

    genres = genre_popularity(df)
    ratings = movie_rating_analysis(df)
    engagement = user_engagement(df)
    actors = actor_popularity(df)
    trend = monthly_trend(df)
    effectiveness = recommendation_effectiveness(df).iloc[0]

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=genres, x="Genre", y="watches", hue="Genre", legend=False, ax=ax)
    ax.set_title("Genre Popularity by Watch Count")
    ax.set_xlabel("Genre")
    ax.set_ylabel("Watch Count")
    ax.tick_params(axis="x", rotation=25)
    add_labels(ax)
    save_plot(fig, "01_genre_popularity.png")

    fig, ax = plt.subplots(figsize=(10, 5))
    top_movies = ratings.sort_values(["avg_rating", "watches"], ascending=False).head(10)
    sns.barplot(data=top_movies, y="Movie", x="avg_rating", hue="Movie", legend=False, ax=ax)
    ax.set_title("Top Rated Movies")
    ax.set_xlabel("Average Rating")
    ax.set_ylabel("")
    ax.set_xlim(0, 5)
    add_labels(ax, orient="horizontal")
    save_plot(fig, "02_top_rated_movies.png")

    fig, ax = plt.subplots(figsize=(10, 5))
    low_movies = ratings.sort_values(["avg_rating", "watches"]).head(10)
    sns.barplot(data=low_movies, y="Movie", x="avg_rating", hue="Movie", legend=False, ax=ax)
    ax.set_title("Lowest Rated Movies")
    ax.set_xlabel("Average Rating")
    ax.set_ylabel("")
    ax.set_xlim(0, 5)
    add_labels(ax, orient="horizontal")
    save_plot(fig, "03_lowest_rated_movies.png")

    fig, ax = plt.subplots(figsize=(11, 5))
    top_users = engagement.head(10)
    sns.barplot(
        data=top_users,
        y="User_Name",
        x="total_watch_time",
        hue="User_Name",
        legend=False,
        ax=ax,
    )
    ax.set_title("Top 10 Users by Watch Time")
    ax.set_xlabel("Total Watch Time (Minutes)")
    ax.set_ylabel("")
    add_labels(ax, orient="horizontal")
    save_plot(fig, "04_top_user_engagement.png")

    fig, ax = plt.subplots(figsize=(11, 5))
    sns.lineplot(data=trend, x="month", y="total_watch_time", marker="o", linewidth=2.5, ax=ax)
    ax.set_title("Monthly Watch Time Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Watch Time (Minutes)")
    ax.tick_params(axis="x", rotation=30)
    save_plot(fig, "05_monthly_watch_time_trend.png")

    fig, ax = plt.subplots(figsize=(7, 5))
    watched_rate = effectiveness["watch_rate"]
    ax.pie(
        [watched_rate, 100 - watched_rate],
        labels=["Watched Recommended Movie", "Not Watched"],
        autopct="%1.1f%%",
        startangle=90,
        colors=sns.color_palette("Set2", 2),
    )
    ax.set_title("Recommendation Effectiveness")
    save_plot(fig, "06_recommendation_effectiveness.png")

    fig, ax = plt.subplots(figsize=(11, 5))
    top_actors = actors.head(10)
    sns.barplot(data=top_actors, y="Actor", x="watches", hue="Actor", legend=False, ax=ax)
    ax.set_title("Top Actors by Watch Count")
    ax.set_xlabel("Watch Count")
    ax.set_ylabel("")
    add_labels(ax, orient="horizontal")
    save_plot(fig, "07_top_actors_watch_count.png")

    fig, ax = plt.subplots(figsize=(11, 5))
    actor_rating = actors.sort_values(["avg_rating", "watches"], ascending=False).head(10)
    sns.barplot(data=actor_rating, y="Actor", x="avg_rating", hue="Actor", legend=False, ax=ax)
    ax.set_title("Top Actors by Average Rating")
    ax.set_xlabel("Average Rating")
    ax.set_ylabel("")
    ax.set_xlim(0, 5)
    add_labels(ax, orient="horizontal")
    save_plot(fig, "08_top_actors_average_rating.png")

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(
        data=ratings,
        x="avg_rating",
        y="avg_engagement",
        size="watches",
        hue="watches",
        sizes=(80, 700),
        palette="viridis",
        ax=ax,
    )
    for _, row in ratings.iterrows():
        ax.text(row["avg_rating"] + 0.01, row["avg_engagement"], row["Movie"], fontsize=8)
    ax.set_title("Movie Rating vs Engagement")
    ax.set_xlabel("Average Rating")
    ax.set_ylabel("Average Engagement Score")
    ax.legend(title="Watches", loc="best")
    save_plot(fig, "09_rating_vs_engagement.png")


if __name__ == "__main__":
    main()
