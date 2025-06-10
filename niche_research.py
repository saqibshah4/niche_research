import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

API_KEY = "AIzaSyBzYsHPzUqV8bpW6LGhRSmUYNsjQQr_tgY"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

st.title("🔍 Viral Niche Finder Tool")

days = st.slider("🗓️ Enter Days to Search", 1, 30, 7)
min_views = st.number_input("📈 Minimum Views", min_value=1000, value=10000)
max_subs = st.number_input("👤 Maximum Subscribers", min_value=100, value=3000)

# Define keywords and categories
niche_keywords = {
    "Affair & Relationships": ["Affair Relationship Stories", "Reddit Relationship Advice", "Open Marriage"],
    "Reddit Drama": ["Reddit Update", "Reddit Cheating", "AITA Update", "AskReddit Surviving Infidelity"],
    "Infidelity": ["Surviving Infidelity", "Reddit Cheating Story", "Cheating Story Actually Happened"]
}

if st.button("🔎 Find Viral Niches"):
    start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
    results = []

    for niche, keywords in niche_keywords.items():
        for keyword in keywords:
            st.write(f"Searching keyword in **{niche}**: {keyword}")

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY
            }

            search_response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            search_data = search_response.json()

            if "items" not in search_data:
                continue

            videos = search_data["items"]
            video_ids = [v["id"]["videoId"] for v in videos if "id" in v and "videoId" in v["id"]]
            channel_ids = [v["snippet"]["channelId"] for v in videos]

            if not video_ids:
                continue

            video_stats = requests.get(YOUTUBE_VIDEO_URL, params={
                "part": "statistics",
                "id": ",".join(video_ids),
                "key": API_KEY
            }).json()

            channel_stats = requests.get(YOUTUBE_CHANNEL_URL, params={
                "part": "statistics",
                "id": ",".join(channel_ids),
                "key": API_KEY
            }).json()

            for i, video in enumerate(videos):
                try:
                    stats = video_stats["items"][i]["statistics"]
                    channel_stat = channel_stats["items"][i]["statistics"]

                    view_count = int(stats.get("viewCount", 0))
                    subs = int(channel_stat.get("subscriberCount", 0))

                    if view_count >= min_views and subs <= max_subs:
                        results.append({
                            "Niche": niche,
                            "Title": video["snippet"]["title"],
                            "Description": video["snippet"]["description"][:150],
                            "URL": f"https://www.youtube.com/watch?v={video['id']['videoId']}",
                            "Views": view_count,
                            "Subscribers": subs
                        })
                except Exception as e:
                    continue

    if results:
        df = pd.DataFrame(results)
        st.success(f"✅ Found {len(df)} potential viral niche videos!")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", data=csv, file_name="viral_niches.csv", mime='text/csv')
    else:
        st.warning("❌ No results found with current filters.")
