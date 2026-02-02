import streamlit as st
import requests

st.set_page_config(page_title="나와 어울리는 영화는?", page_icon="🎬")

# ======================
# 사이드바 - API Key 입력
# ======================
st.sidebar.title("🔑 TMDB 설정")
api_key = st.sidebar.text_input("TMDB API Key 입력", type="password")

# ======================
# 제목 & 소개
# ======================
st.title("🎬 나와 어울리는 영화는?")
st.write(
    "5가지 질문을 통해 **당신의 영화 취향**을 분석하고,\n"
    "취향에 꼭 맞는 영화를 추천해드립니다 🍿"
)

st.divider()

# ======================
# 장르 및 점수 구조
# ======================
genres = {
    "로맨스/드라마": {"id": [18, 10749], "score": 0},
    "액션/어드벤처": {"id": [28], "score": 0},
    "SF/판타지": {"id": [878, 14], "score": 0},
    "코미디": {"id": [35], "score": 0},
}

# ======================
# 질문
# ======================
questions = [
    (
        "Q1. 시험이 끝난 금요일 밤, 가장 끌리는 계획은?",
        [
            ("조용한 카페나 방에서 감정선 깊은 영화 한 편", "로맨스/드라마"),
            ("팝콘 들고 화끈한 액션 영화 보면서 스트레스 풀기", "액션/어드벤처"),
            ("현실을 잠시 잊게 해줄 새로운 세계관의 영화 몰아보기", "SF/판타지"),
            ("친구들이랑 웃다가 배 아픈 코미디 영화 보기", "코미디"),
        ],
    ),
    (
        "Q2. 영화 속 주인공에게 가장 끌리는 타입은?",
        [
            ("감정 변화가 섬세하고 관계에 진심인 인물", "로맨스/드라마"),
            ("위기 상황에서도 몸부터 움직이는 행동파", "액션/어드벤처"),
            ("특별한 능력이나 비범한 운명을 가진 존재", "SF/판타지"),
            ("어딘가 허술한데 묘하게 정이 가는 캐릭터", "코미디"),
        ],
    ),
    (
        "Q3. 너의 일상에 가장 필요한 영화의 역할은?",
        [
            ("마음을 건드려서 생각할 거리를 주는 것", "로맨스/드라마"),
            ("지루한 일상에 아드레날린을 넣어주는 것", "액션/어드벤처"),
            ("상상력을 자극하고 새로운 시각을 주는 것", "SF/판타지"),
            ("아무 생각 없이 웃고 기분 좋아지게 하는 것", "코미디"),
        ],
    ),
    (
        "Q4. 영화가 끝났을 때 가장 좋은 여운은?",
        [
            ("한동안 장면과 대사가 머릿속에서 맴도는 느낌", "로맨스/드라마"),
            ("“와… 이 장면 미쳤다” 하면서 바로 다시 보고 싶어지는 느낌", "액션/어드벤처"),
            ("세계관 설정을 찾아보고 싶어지는 궁금증", "SF/판타지"),
            ("명장면이 밈처럼 계속 떠올라 웃음이 나는 상태", "코미디"),
        ],
    ),
    (
        "Q5. 친구가 “이 영화 꼭 봐”라고 추천했을 때, 네가 가장 혹하는 말은?",
        [
            ("스토리가 진짜 현실적이고 감정선이 미쳤어", "로맨스/드라마"),
            ("액션이 장난 아니고 전개가 숨 돌릴 틈이 없어", "액션/어드벤처"),
            ("설정이 완전 새롭고 상상력이 터져", "SF/판타지"),
            ("진짜 아무 생각 없이 웃다가 끝나", "코미디"),
        ],
    ),
]

answers = []

for q, options in questions:
    choice = st.radio(
        q,
        [opt[0] for opt in options],
        index=None,
    )
    answers.append((choice, options))

st.divider()

# ======================
# 결과 버튼
# ======================
if st.button("🎥 결과 보기"):
    if not api_key:
        st.error("TMDB API Key를 사이드바에 입력해주세요.")
    elif any(a[0] is None for a in answers):
        st.warning("모든 질문에 답변해주세요!")
    else:
        # 점수 계산
        for answer, options in answers:
            for text, genre in options:
                if answer == text:
                    genres[genre]["score"] += 1

        # 최고 점수 장르 선택
        best_genre = max(genres, key=lambda g: genres[g]["score"])
        genre_ids = genres[best_genre]["id"]

        st.subheader(f"🎯 당신의 영화 취향: {best_genre}")
        st.write("당신의 답변을 바탕으로 아래 영화를 추천했어요!")

        # ======================
        # TMDB API 호출
        # ======================
        genre_query = ",".join(map(str, genre_ids))
        url = (
            f"https://api.themoviedb.org/3/discover/movie"
            f"?api_key={api_key}&with_genres={genre_query}&language=ko-KR"
        )

        response = requests.get(url)
        data = response.json()
        movies = data.get("results", [])[:5]

        # ======================
        # 영화 출력
        # ======================
        for movie in movies:
            st.divider()
            cols = st.columns([1, 2])

            with cols[0]:
                if movie.get("poster_path"):
                    st.image(
                        "https://image.tmdb.org/t/p/w500" + movie["poster_path"],
                        use_container_width=True,
                    )

            with cols[1]:
                st.markdown(f"### 🎬 {movie['title']}")
                st.write(f"⭐ 평점: {movie['vote_average']}")
                st.write(movie["overview"] or "줄거리 정보가 없습니다.")
                st.info(
                    f"💡 이 영화를 추천하는 이유:\n"
                    f"{best_genre} 성향의 분위기와 잘 어울리는 인기 작품이에요."
                )



            



