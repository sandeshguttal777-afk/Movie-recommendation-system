from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

from src.analytics import (
    actor_popularity,
    genre_popularity,
    kpis,
    load_movies,
    monthly_trend,
    movie_rating_analysis,
    recommendation_effectiveness,
    recommend_movies,
    user_engagement,
    user_preferences,
)


st.set_page_config(page_title="Movie Recommendation Dashboard", layout="wide")
sns.set_theme(style="whitegrid")


@st.cache_data
def get_data():
    return load_movies()


@st.cache_data
def get_uploaded_data(uploaded_file):
    return load_movies(uploaded_file)


default_df = get_data()

st.title("Movie Recommendation System")
st.caption("Preference analysis, recommendation performance, genre trends, ratings, engagement, and actor popularity.")

with st.sidebar:
    st.header("Filters")
    uploaded_file = st.file_uploader("Upload movie CSV", type=["csv"])

df = get_uploaded_data(uploaded_file) if uploaded_file is not None else default_df


def fmt(value, digits=2):
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def insight_box(title, items):
    st.markdown(f"**{title}**")
    for item in items:
        st.markdown(f"- {item}")


with st.sidebar:
    if uploaded_file is not None:
        st.success(f"Using uploaded file: {uploaded_file.name}")
    else:
        st.info("Using default project CSV")

    genres = st.multiselect("Genre", sorted(df["Genre"].unique()))
    cities = st.multiselect("City", sorted(df["City"].unique()))
    platforms = st.multiselect("OTT Platform", sorted(df["OTT_Platform"].unique()))
    users = df[["User_ID", "User_Name"]].drop_duplicates().sort_values("User_ID")
    user_label = st.selectbox(
        "User for recommendations",
        users.apply(lambda row: f"{row.User_ID} - {row.User_Name}", axis=1),
    )
    selected_user_id = int(user_label.split(" - ")[0])

filtered = df.copy()
if genres:
    filtered = filtered[filtered["Genre"].isin(genres)]
if cities:
    filtered = filtered[filtered["City"].isin(cities)]
if platforms:
    filtered = filtered[filtered["OTT_Platform"].isin(platforms)]

metrics = kpis(filtered)
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Interactions", f"{metrics['total_interactions']:,}")
col2.metric("Users", f"{metrics['unique_users']:,}")
col3.metric("Movies", f"{metrics['unique_movies']:,}")
col4.metric("Avg Rating", metrics["avg_rating"])
col5.metric("Avg Watch Min", metrics["avg_watch_time"])
col6.metric("Rec Watch Rate", f"{metrics['recommendation_watch_rate']}%")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "Preferences",
        "Recommendations",
        "Genres",
        "Ratings",
        "Engagement",
        "Effectiveness",
        "Actors",
    ]
)

with tab1:
    st.subheader("User Movie Preference Analysis")
    prefs = user_preferences(filtered, selected_user_id)
    if prefs.empty:
        st.warning("No preference records found for the selected filters.")
    else:
        top_pref = prefs.iloc[0]
        insight_box(
            "Preference Insights",
            [
                f"{top_pref['User_Name']} prefers {top_pref['Genre']} most, with {int(top_pref['watches'])} watch record(s).",
                f"The selected user's strongest genre has an average rating of {fmt(top_pref['avg_rating'])} and {int(top_pref['total_watch_time'])} total watch minutes.",
                f"Average engagement for this top preference is {fmt(top_pref['avg_engagement'], 3)} on the dashboard engagement scale.",
            ],
        )
    st.dataframe(prefs, use_container_width=True, hide_index=True)

    if not prefs.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(data=prefs, x="Genre", y="total_watch_time", hue="Genre", legend=False, ax=ax)
        ax.set_xlabel("")
        ax.set_ylabel("Total watch time")
        ax.tick_params(axis="x", rotation=30)
        st.pyplot(fig)

with tab2:
    st.subheader("Personalized Movie Recommendation Analysis")
    recs = recommend_movies(df, selected_user_id, limit=10)
    if recs.empty:
        st.warning("No recommendations are available for the selected user.")
    else:
        best_rec = recs.iloc[0]
        insight_box(
            "Recommendation Insights",
            [
                f"Top recommendation: {best_rec['Movie']} with a score of {fmt(best_rec['recommendation_score'])}.",
                f"The recommendation is influenced by {best_rec['Genre']} genre fit, actor/platform affinity, wishlist overlap, and historical popularity.",
                f"Recommended titles have an average rating range from {fmt(recs['avg_rating'].min())} to {fmt(recs['avg_rating'].max())}.",
            ],
        )
    st.dataframe(recs, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Genre Popularity Analysis")
    genres_df = genre_popularity(filtered)
    if genres_df.empty:
        st.warning("No genre records found for the selected filters.")
    else:
        top_genre = genres_df.iloc[0]
        highest_rated_genre = genres_df.sort_values(["avg_rating", "watches"], ascending=False).iloc[0]
        insight_box(
            "Genre Insights",
            [
                f"{top_genre['Genre']} is the most watched genre with {int(top_genre['watches'])} watches.",
                f"{highest_rated_genre['Genre']} has the strongest average rating at {fmt(highest_rated_genre['avg_rating'])}.",
                f"The leading genre generated {int(top_genre['total_watch_time'])} total watch minutes.",
            ],
        )
    st.dataframe(genres_df, use_container_width=True, hide_index=True)

    if not genres_df.empty:
        fig, ax = plt.subplots(figsize=(9, 4))
        sns.barplot(data=genres_df, x="Genre", y="watches", hue="Genre", legend=False, ax=ax)
        ax.set_xlabel("")
        ax.set_ylabel("Watches")
        ax.tick_params(axis="x", rotation=30)
        st.pyplot(fig)

with tab4:
    st.subheader("Movie Rating Analysis")
    ratings = movie_rating_analysis(filtered)
    if ratings.empty:
        st.warning("No rating records found for the selected filters.")
    else:
        top_movie = ratings.iloc[0]
        low_movie = ratings.sort_values(["avg_rating", "watches"]).iloc[0]
        most_watched_movie = ratings.sort_values(["watches", "avg_rating"], ascending=False).iloc[0]
        insight_box(
            "Rating Insights",
            [
                f"Highest rated movie: {top_movie['Movie']} with an average rating of {fmt(top_movie['avg_rating'])}.",
                f"Lowest rated movie: {low_movie['Movie']} with an average rating of {fmt(low_movie['avg_rating'])}.",
                f"Most watched movie: {most_watched_movie['Movie']} with {int(most_watched_movie['watches'])} watches.",
            ],
        )
    top_col, low_col = st.columns(2)
    top_col.markdown("**Highly Rated Movies**")
    top_col.dataframe(ratings.head(10), use_container_width=True, hide_index=True)
    low_col.markdown("**Low Rated Movies**")
    low_col.dataframe(ratings.sort_values(["avg_rating", "watches"]).head(10), use_container_width=True, hide_index=True)

with tab5:
    st.subheader("User Engagement Analysis")
    engagement = user_engagement(filtered)
    if engagement.empty:
        st.warning("No engagement records found for the selected filters.")
    else:
        top_user = engagement.iloc[0]
        avg_total_watch = engagement["total_watch_time"].mean()
        insight_box(
            "Engagement Insights",
            [
                f"Most engaged user: {top_user['User_Name']} with {int(top_user['total_watch_time'])} total watch minutes.",
                f"Average total watch time per user is {fmt(avg_total_watch, 1)} minutes.",
                f"Top user engagement combines {int(top_user['movies_watched'])} movie record(s), {fmt(top_user['avg_rating'])} average rating, and {fmt(top_user['avg_engagement'], 3)} engagement score.",
            ],
        )
    st.dataframe(engagement.head(25), use_container_width=True, hide_index=True)

    trend = monthly_trend(filtered)
    if not trend.empty:
        peak_month = trend.sort_values("total_watch_time", ascending=False).iloc[0]
        st.info(f"Peak month: {peak_month['month'].strftime('%B %Y')} with {int(peak_month['total_watch_time'])} watch minutes.")
        fig, ax = plt.subplots(figsize=(9, 4))
        sns.lineplot(data=trend, x="month", y="total_watch_time", marker="o", ax=ax)
        ax.set_xlabel("")
        ax.set_ylabel("Total watch time")
        st.pyplot(fig)

with tab6:
    st.subheader("Recommendation Effectiveness Analysis")
    effectiveness = recommendation_effectiveness(filtered)
    eff = effectiveness.iloc[0]
    insight_box(
        "Effectiveness Insights",
        [
            f"{int(eff['watched_recommendation_count'])} out of {int(eff['recommended_count'])} recommendations were later found in watch history.",
            f"The recommendation watch-through rate is {fmt(eff['watch_rate'])}%.",
            f"When recommendations were watched, users averaged {fmt(eff['avg_rating_when_watched'])} rating and {fmt(eff['avg_watch_time_when_watched'], 1)} watch minutes.",
        ],
    )
    st.dataframe(effectiveness, use_container_width=True, hide_index=True)

    watched_rate = effectiveness["watch_rate"].iloc[0]
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.pie([watched_rate, 100 - watched_rate], labels=["Watched", "Not watched"], autopct="%1.1f%%")
    ax.set_title("Recommended Movie Follow-through")
    st.pyplot(fig)

with tab7:
    st.subheader("Top Actors Popularity Analysis")
    actors = actor_popularity(filtered)
    if actors.empty:
        st.warning("No actor records found for the selected filters.")
    else:
        top_actor = actors.iloc[0]
        highest_rated_actor = actors.sort_values(["avg_rating", "watches"], ascending=False).iloc[0]
        insight_box(
            "Actor Insights",
            [
                f"Most watched actor: {top_actor['Actor']} with {int(top_actor['watches'])} watches across {int(top_actor['unique_movies'])} unique movies.",
                f"Highest rated actor: {highest_rated_actor['Actor']} with an average rating of {fmt(highest_rated_actor['avg_rating'])}.",
                f"{top_actor['Actor']} generated {int(top_actor['total_watch_time'])} total watch minutes and {fmt(top_actor['avg_engagement'], 3)} average engagement.",
            ],
        )
    st.dataframe(actors.head(20), use_container_width=True, hide_index=True)

    if not actors.empty:
        fig, ax = plt.subplots(figsize=(9, 4))
        top_actors = actors.head(10)
        sns.barplot(data=top_actors, y="Actor", x="watches", hue="Actor", legend=False, ax=ax)
        ax.set_xlabel("Watches")
        ax.set_ylabel("")
        st.pyplot(fig)
