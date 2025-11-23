"""
Streamlit UI for News Scraper API

Run with: uv run streamlit run streamlit_app.py
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import json

# API Configuration
API_BASE = "http://localhost:8000/api/v1"

# Page Configuration
st.set_page_config(
    page_title="News Scraper API",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .stat-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 0.5rem 0;
    }
    .article-card {
        padding: 1rem;
        border-left: 4px solid #1E88E5;
        background-color: #f8f9fa;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)


def check_api_health():
    """Check if API is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_sources():
    """Get available news sources."""
    try:
        response = requests.get(f"{API_BASE}/sources")
        if response.status_code == 200:
            return response.json().get("sources", [])
    except:
        pass
    return []


def scrape_articles(sources, max_articles, date_from=None, date_to=None):
    """Trigger article scraping."""
    payload = {
        "sources": sources,
        "max_articles": max_articles
    }

    if date_from:
        payload["date_from"] = date_from.isoformat()
    if date_to:
        payload["date_to"] = date_to.isoformat()

    try:
        response = requests.post(f"{API_BASE}/scrape", json=payload, timeout=300)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_articles(category=None, time_period=None, keyword=None, min_relevance=None, limit=50):
    """Fetch articles with filters."""
    params = {"limit": limit}

    if category:
        params["category"] = category
    if time_period:
        params["time_period"] = time_period
    if keyword:
        params["keyword"] = keyword
    if min_relevance:
        params["min_relevance"] = min_relevance

    try:
        response = requests.get(f"{API_BASE}/articles", params=params)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []


def get_stats():
    """Get API statistics."""
    try:
        response = requests.get(f"{API_BASE}/stats")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {}


# Main App
def main():
    # Header
    st.markdown('<p class="main-header">📰 News Scraper API Dashboard</p>', unsafe_allow_html=True)

    # Check API health
    api_healthy = check_api_health()

    if not api_healthy:
        st.error("⚠️ API is not running! Please start the server with: `uv run python run.py`")
        st.stop()

    st.success("✅ API is running")

    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["🏠 Home", "🔍 Scrape Articles", "📊 View Articles", "📈 Statistics"]
    )

    # HOME PAGE
    if page == "🏠 Home":
        st.header("Welcome to News Scraper API")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.info("**🔍 Multi-Source Scraping**\n\nScrape from NYT, Reuters, OpenAI, Google Research")

        with col2:
            st.info("**🤖 NLP Analysis**\n\nAutomatic keyword extraction and categorization")

        with col3:
            st.info("**📅 Time Periods**\n\n2002-2018, 2018-2022, 2023-2024")

        st.markdown("---")

        # Quick Stats
        stats = get_stats()
        if stats:
            st.subheader("Quick Statistics")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Articles", stats.get("total_articles", 0))

            with col2:
                st.metric("Energy", stats.get("by_category", {}).get("energy", 0))

            with col3:
                st.metric("AI", stats.get("by_category", {}).get("ai", 0))

            with col4:
                st.metric("Financial", stats.get("by_category", {}).get("financial", 0))

        st.markdown("---")

        st.subheader("Quick Start Guide")
        st.markdown("""
        1. **🔍 Scrape Articles**: Navigate to the scrape page to fetch news from various sources
        2. **📊 View Articles**: Browse and filter scraped articles by category, time period, or keywords
        3. **📈 Statistics**: View comprehensive analytics about your scraped data

        **Categories:**
        - **Energy**: electricity, power grid, outages, renewable energy
        - **Financial**: economy, markets, cryptocurrency, trading
        - **AI**: machine learning, deep learning, automation, GPT
        """)

    # SCRAPE PAGE
    elif page == "🔍 Scrape Articles":
        st.header("Scrape News Articles")

        sources = get_sources()

        if not sources:
            st.error("Could not fetch available sources")
            return

        col1, col2 = st.columns(2)

        with col1:
            selected_sources = st.multiselect(
                "Select News Sources",
                sources,
                default=["nyt", "reuters"]
            )

        with col2:
            max_articles = st.slider(
                "Max Articles per Source",
                min_value=5,
                max_value=100,
                value=20,
                step=5
            )

        col3, col4 = st.columns(2)

        with col3:
            use_date_filter = st.checkbox("Filter by Date Range")
            if use_date_filter:
                date_from = st.date_input(
                    "From Date",
                    value=datetime(2023, 1, 1)
                )
            else:
                date_from = None

        with col4:
            if use_date_filter:
                st.write("")  # Spacing
                st.write("")  # Spacing
                date_to = st.date_input(
                    "To Date",
                    value=datetime.now()
                )
            else:
                date_to = None

        st.markdown("---")

        if st.button("🚀 Start Scraping", type="primary", use_container_width=True):
            if not selected_sources:
                st.error("Please select at least one source")
                return

            with st.spinner("Scraping articles... This may take a few minutes..."):
                result = scrape_articles(
                    selected_sources,
                    max_articles,
                    date_from,
                    date_to
                )

            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.success(f"✅ {result.get('message', 'Scraping completed')}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Articles Scraped", result.get("articles_scraped", 0))
                with col2:
                    st.metric("Articles Stored", result.get("articles_stored", 0))
                with col3:
                    st.metric("Status", result.get("status", "unknown").upper())

    # VIEW ARTICLES PAGE
    elif page == "📊 View Articles":
        st.header("Browse Articles")

        # Filters
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            category_filter = st.selectbox(
                "Category",
                ["All", "energy", "financial", "ai"]
            )
            category = None if category_filter == "All" else category_filter

        with col2:
            time_period_filter = st.selectbox(
                "Time Period",
                ["All", "2002-2018", "2018-2022", "2023-2024"]
            )
            time_period = None if time_period_filter == "All" else time_period_filter

        with col3:
            keyword = st.text_input("Keyword Search")
            keyword = keyword if keyword else None

        with col4:
            min_relevance = st.slider(
                "Min Relevance Score",
                min_value=0,
                max_value=20,
                value=0
            )
            min_relevance = min_relevance if min_relevance > 0 else None

        limit = st.slider("Number of Articles", 10, 100, 50, 10)

        st.markdown("---")

        # Fetch articles
        articles = get_articles(category, time_period, keyword, min_relevance, limit)

        if not articles:
            st.info("No articles found. Try adjusting your filters or scrape some articles first.")
            return

        st.subheader(f"Found {len(articles)} articles")

        # Display format selector
        display_format = st.radio(
            "Display Format",
            ["Cards", "Table"],
            horizontal=True
        )

        if display_format == "Cards":
            for article in articles:
                with st.container():
                    st.markdown(f"""
                    <div class="article-card">
                        <h3>{article.get('title', 'No Title')}</h3>
                        <p><strong>Source:</strong> {article.get('source', 'Unknown')}</p>
                        <p><strong>Published:</strong> {article.get('published_date', 'Unknown')}</p>
                        <p><strong>Time Period:</strong> {article.get('time_period', 'N/A')}</p>
                        <p><strong>Categories:</strong> {', '.join(article.get('categories', []))}</p>
                        <p><strong>Relevance Score:</strong> {article.get('relevance_score', 0)}</p>
                        <p><strong>Keywords:</strong> {', '.join(article.get('keywords', [])[:10])}</p>
                        <p><strong>URL:</strong> <a href="{article.get('url', '#')}" target="_blank">Read Article</a></p>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander("View Summary"):
                        st.write(article.get('summary', 'No summary available'))

        else:  # Table format
            df_data = []
            for article in articles:
                df_data.append({
                    "Title": article.get('title', '')[:50] + "...",
                    "Source": article.get('source', ''),
                    "Date": article.get('published_date', ''),
                    "Period": article.get('time_period', ''),
                    "Categories": ', '.join(article.get('categories', [])),
                    "Relevance": article.get('relevance_score', 0),
                    "URL": article.get('url', '')
                })

            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

    # STATISTICS PAGE
    elif page == "📈 Statistics":
        st.header("Analytics Dashboard")

        stats = get_stats()

        if not stats:
            st.error("Could not fetch statistics")
            return

        # Overall Stats
        st.subheader("Overview")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Articles", stats.get("total_articles", 0))

        with col2:
            date_range = stats.get("date_range", {})
            earliest = date_range.get("earliest")
            if earliest and earliest != "N/A":
                earliest = earliest[:10]
            else:
                earliest = "N/A"
            st.metric("Earliest Article", earliest)

        with col3:
            latest = date_range.get("latest")
            if latest and latest != "N/A":
                latest = latest[:10]
            else:
                latest = "N/A"
            st.metric("Latest Article", latest)

        with col4:
            num_sources = len(stats.get("by_source", {}))
            st.metric("Sources", num_sources)

        st.markdown("---")

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Articles by Category")
            category_data = stats.get("by_category", {})
            if category_data:
                df_cat = pd.DataFrame({
                    "Category": list(category_data.keys()),
                    "Count": list(category_data.values())
                })
                st.bar_chart(df_cat.set_index("Category"))
            else:
                st.info("No category data available")

        with col2:
            st.subheader("Articles by Time Period")
            period_data = stats.get("by_time_period", {})
            if period_data:
                df_period = pd.DataFrame({
                    "Period": list(period_data.keys()),
                    "Count": list(period_data.values())
                })
                st.bar_chart(df_period.set_index("Period"))
            else:
                st.info("No time period data available")

        st.markdown("---")

        # Source breakdown
        st.subheader("Articles by Source")
        source_data = stats.get("by_source", {})
        if source_data:
            df_source = pd.DataFrame({
                "Source": list(source_data.keys()),
                "Count": list(source_data.values())
            }).sort_values("Count", ascending=False)

            st.dataframe(df_source, use_container_width=True, hide_index=True)
        else:
            st.info("No source data available")

        # Raw JSON
        with st.expander("View Raw JSON Data"):
            st.json(stats)


if __name__ == "__main__":
    main()
