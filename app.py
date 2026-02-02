import streamlit as st
import requests

st.title("🎬 TMDB API 테스트")

# 사이드바에서 API 키 입력
TMDB_API_KEY = st.sidebar.text_input("TMDB API Key", type="password")

if TMDB_API_KEY:
    if st.button("인기 영화 가져오기"):
        # TMDB에서 인기 영화 가져오기
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=ko-KR"
        response = requests.get(url)
        data = response.json()
        
        # 첫 번째 영화 정보 출력
        movie = data['results'][0]
        st.write(f"🎬 제목: {movie['title']}")
        st.write(f"⭐ 평점: {movie['vote_average']}/10")
        st.write(f"📅 개봉일: {movie['release_date']}")
        st.write(f"📝 줄거리: {movie['overview'][:100]}...")
else:
    st.info("사이드바에 TMDB API Key를 입력해주세요.")
            

