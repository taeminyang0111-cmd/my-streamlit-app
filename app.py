import streamlit as st
import requests
from openai import OpenAI

st.set_page_config(page_title="나와 어울리는 영화는?", page_icon="🎬")

# =========================
# 사이드바 설정
# =========================
st.sidebar.title("⚙️ API 설정")

tmdb_api_key = st.sidebar.text_input("TMDB API Key", type="password")
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

client = None
if openai_api_key:
    client = OpenAI(api_key=openai_api_key)

min_rating = st.sidebar.slider("최소 평점", 0.0, 10.0, 6.5, 0.5)
movie_count = st.sidebar.selectbox("추천 영화 개수", [3, 5, 7], index=1)

# =========================
# 제목
# =========================
st.title("🎬 나와 어울리는 영화는?")
st.write("심리테스트 + AI 추천 이유 생성 기반 영화 추천 서비스 🍿")
st.divider()

# =========================
# 장르 및 질문
# =========================
genres = {
    "로맨스/드라마": {"id": [18, 10749], "score": 0},
    "액션/어드벤처": {"id": [28], "score": 0},
    "SF/판타지": {"id": [878, 14], "score": 0},
    "코미디": {"id": [35], "score": 0},
}

questions = [
    ("Q1. 금요일 밤에 가장 보고 싶은 영화는?",
     [("감정선 깊은 영화", "로맨스/드라마"),
      ("시원한 액션 영화", "액션/어드벤처"),
      ("세계관이 독특한 영화", "SF/판타지"),
      ("가볍게 웃긴 영화", "코미디")]),

    ("Q2. 영화에서 가장 중요한 요소는?",
     [("감정과 관계", "로맨스/드라마"),
      ("속도감과 긴장감", "액션/어드벤처"),
      ("설정과 상상력", "SF/판타지"),
      ("웃음과 분위기", "코미디")]),

    ("Q3. 주인공 성향 중 끌리는 것은?",
     [("섬세하고 현실적인 인물", "로맨스/드라마"),
      ("몸이 먼저 움직이는 인물", "액션/어드벤처"),
      ("특별한 능력을 가진 인물", "SF/판타지"),
      ("허술하지만 정 가는 인물", "코미디")]),

    ("Q4. 영화가 끝난 뒤 가장 좋은 상태는?",
     [("여운이 오래 남는다", "로맨스/드라마"),
      ("다시 보고 싶다", "액션/어드벤처"),
      ("세계관을 찾아본다", "SF/판타지"),
      ("기분이 가벼워진다", "코미디")]),

    ("Q5. 추천 문구 중 끌리는 것은?",
     [("현실 공감", "로맨스/드라마"),
      ("액션 미쳤다", "액션/어드벤처"),
      ("상상력 폭발", "SF/판타지"),
      ("아무 생각 없이 웃김", "코미디")]),
]

answers = []
for q, opts in questions:
    choice = st.radio(q, [o[0] for o in opts], index=None)
    answers.append((choice, opts))

st.divider()

# =========================
# LLM 추천 이유 생성 함수
# =========================
def generate_reason(movie, user_genre):
    prompt = f"""
사용자는 {user_genre} 장르를 선호하는 대학생입니다.
아래 영화가 이 사용자에게 어울리는 이유를 2~3문장으로 설명해주세요.

영화 제목: {movie['title']}
평점: {movie['vote_average']}
줄거리: {movie['overview']}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 영화 추천을 잘하는 친절한 AI야."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()

# =========================
# 결과 버튼
# =========================
if st.button("🎥 결과 보기"):
    if not tmdb_api_key or not openai_api_key:
        st.error("TMDB / OpenAI API Key를 모두 입력해주세요.")
    else:
        # 점수 계산
        for answer, opts in answers:
            for text, genre in opts:
                if answer == text:
                    genres[genre]["score"] += 1

        best_genre = max(genres, key=lambda g: genres[g]["score"])
        genre_ids = ",".join(map(str, genres[best_genre]["id"]))

        st.subheader(f"🎯 당신의 성향: {best_genre}")

        url = (
            f"https://api.themoviedb.org/3/discover/movie"
            f"?api_key={tmdb_api_key}"
            f"&with_genres={genre_ids}"
            f"&vote_average.gte={min_rating}"
            f"&sort_by=popularity.desc"
            f"&language=ko-KR"
        )

        movies = requests.get(url).json().get("results", [])[:movie_count]

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
                st.write(m["overview"] or "줄거리 없음")

                with st.spinner("AI가 추천 이유를 생성 중..."):
                    reason = generate_reason(m, best_genre)

                st.success(f"💡 추천 이유\n\n{reason}")
