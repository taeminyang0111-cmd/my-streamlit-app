import streamlit as st
import requests

st.set_page_config(page_title="나와 어울리는 영화는?", page_icon="🎬")

# =========================
# 사이드바 설정
# =========================
st.sidebar.title("⚙️ 추천 설정")

api_key = st.sidebar.text_input("TMDB API Key", type="password")

min_rating = st.sidebar.slider(
    "최소 평점",
    min_value=0.0,
    max_value=10.0,
    value=6.5,
    step=0.5,
)

year_range = st.sidebar.slider(
    "개봉 연도 범위",
    min_value=1980,
    max_value=2025,
    value=(2010, 2025),
)

movie_count = st.sidebar.selectbox(
    "추천 영화 개수",
    [3, 5, 7, 10],
    index=1,
)

# =========================
# 제목 & 설명
# =========================
st.title("🎬 나와 어울리는 영화는?")
st.write(
    "간단한 심리테스트를 통해 **당신의 영화 취향을 분석**하고,\n"
    "TMDB 데이터를 기반으로 영화를 추천해드립니다 🍿"
)

st.divider()

# =========================
# 장르 설정
# =========================
genres = {
    "로맨스/드라마": {"id": [18, 10749], "score": 0},
    "액션/어드벤처": {"id": [28], "score": 0},
    "SF/판타지": {"id": [878, 14], "score": 0},
    "코미디": {"id": [35], "score": 0},
}

questions = [
    (
        "Q1. 시험이 끝난 금요일 밤, 가장 끌리는 계획은?",
        [
            ("조용한 공간에서 감정선 깊은 영화 한 편", "로맨스/드라마"),
            ("스트레스 날리는 화끈한 액션 영화", "액션/어드벤처"),
            ("현실을 벗어나는 세계관의 영화", "SF/판타지"),
            ("웃다가 끝나는 코미디 영화", "코미디"),
        ],
    ),
    (
        "Q2. 가장 끌리는 영화 주인공은?",
        [
            ("감정이 섬세한 인물", "로맨스/드라마"),
            ("행동력 넘치는 히어로", "액션/어드벤처"),
            ("특별한 능력을 가진 존재", "SF/판타지"),
            ("허당미 있는 캐릭터", "코미디"),
        ],
    ),
    (
        "Q3. 영화에서 가장 중요한 요소는?",
        [
            ("감정과 메시지", "로맨스/드라마"),
            ("속도감과 긴장감", "액션/어드벤처"),
            ("설정과 세계관", "SF/판타지"),
            ("웃음과 분위기", "코미디"),
        ],
    ),
    (
        "Q4. 영화가 끝난 후 가장 좋은 상태는?",
        [
            ("여운이 오래 남는다", "로맨스/드라마"),
            ("명장면이 계속 떠오른다", "액션/어드벤처"),
            ("설정을 더 찾아보고 싶다", "SF/판타지"),
            ("기분이 한결 가볍다", "코미디"),
        ],
    ),
    (
        "Q5. 추천 문구 중 가장 끌리는 것은?",
        [
            ("현실 공감 100%", "로맨스/드라마"),
            ("액션이 미쳤다", "액션/어드벤처"),
            ("상상력이 폭발한다", "SF/판타지"),
            ("아무 생각 없이 웃긴다", "코미디"),
        ],
    ),
]

answers = []
for q, opts in questions:
    choice = st.radio(q, [o[0] for o in opts], index=None)
    answers.append((choice, opts))

st.divider()

# =========================
# 결과 버튼
# =========================
if st.button("🎥 결과 보기"):
    if not api_key:
        st.error("TMDB API Key를 입력해주세요.")
    elif any(a[0] is None for a in answers):
        st.warning("모든 질문에 답해주세요!")
    else:
        # 점수 계산
        for answer, opts in answers:
            for text, genre in opts:
                if answer == text:
                    genres[genre]["score"] += 1

        best_genre = max(genres, key=lambda g: genres[g]["score"])
        genre_ids = ",".join(map(str, genres[best_genre]["id"]))

        st.subheader(f"🎯 당신의 영화 취향: **{best_genre}**")
        st.write("아래는 당신의 취향 + 설정을 반영한 추천 영화입니다.")

        # =========================
        # TMDB Discover API
        # =========================
        url = (
            f"https://api.themoviedb.org/3/discover/movie"
            f"?api_key={api_key}"
            f"&with_genres={genre_ids}"
            f"&primary_release_date.gte={year_range[0]}-01-01"
            f"&primary_release_date.lte={year_range[1]}-12-31"
            f"&vote_average.gte={min_rating}"
            f"&sort_by=popularity.desc"
            f"&language=ko-KR"
        )

        res = requests.get(url).json()
        movies = res.get("results", [])[:movie_count]

        # =========================
        # 영화 출력
        # =========================
        for m in movies:
            st.divider()
            col1, col2 = st.columns([1, 2])

            with col1:
                if m.get("poster_path"):
                    st.image(
                        "https://image.tmdb.org/t/p/w500" + m["poster_path"],
                        use_container_width=True,
                    )

            with col2:
                st.markdown(f"### 🎬 {m['title']}")
                st.write(f"⭐ 평점: {m['vote_average']}")
                st.write(m["overview"] or "줄거리 정보 없음")

                st.info(
                    f"💡 추천 이유\n"
                    f"- 당신의 **{best_genre} 성향**과 잘 맞고\n"
                    f"- 평점 {min_rating} 이상, 최근 인기가 높은 작품이에요."
                )
