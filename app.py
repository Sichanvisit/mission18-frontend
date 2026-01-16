import streamlit as st
import requests

# [수정] 본인의 Render 백엔드 URL을 입력하세요.
BACKEND_URL = "https://mission18-backend.onrender.com"

st.set_page_config(page_title="영화 리뷰 AI 서비스", layout="wide")
st.title("🎬 영화 정보 & AI 감성 리뷰 서비스")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["영화 목록", "영화 추가", "리뷰 작성/보기"])

# --- 탭 1: 영화 목록 ---
with tab1:
    st.header("현재 등록된 영화")
    try:
        response = requests.get(f"{BACKEND_URL}/movies")
        if response.status_code == 200:
            movies = response.json()
            if not movies:
                st.info("등록된 영화가 없습니다. '영화 추가' 탭에서 등록해주세요.")
            else:
                cols = st.columns(3)  # 3열로 배치
                for idx, movie in enumerate(movies):
                    with cols[idx % 3]:
                        if movie['poster_url']:
                            st.image(movie['poster_url'], use_container_width=True)
                        st.subheader(f"{movie['id']}. {movie['title']}")
                        st.text(f"감독: {movie['director']}")
                        st.text(f"장르: {movie['genre']}")
        else:
            st.error("영화 목록을 불러오지 못했습니다.")
    except Exception as e:
        st.error(f"서버 연결 오류: {e}")

# --- 탭 2: 영화 추가 ---
with tab2:
    st.header("새로운 영화 등록")
    with st.form("movie_form"):
        title = st.text_input("영화 제목")
        director = st.text_input("감독")
        genre_list = st.multiselect("장르 (여러 개 선택 가능)", 
                            ["액션", "로맨스", "SF", "공포", "드라마", "애니메이션", "코미디", "스릴러", "판타지"])
        poster_url = st.text_input("포스터 이미지 URL")
        
        submitted = st.form_submit_button("영화 등록하기")
        if submitted:
            new_movie = {
                "title": title,
                "director": director,
                "genre": ", ".join(genre_list),
                "poster_url": poster_url
            }
            res = requests.post(f"{BACKEND_URL}/movies", json=new_movie)
            if res.status_code == 200:
                st.success(f"'{title}' 등록 성공!")
                st.rerun()  # 목록 갱신을 위해 재실행
            else:
                st.error("등록 실패")

# --- 탭 3: 리뷰 작성 및 보기 ---
with tab3:
    st.header("리뷰 작성 및 AI 분석")
    
    try:
        movies_res = requests.get(f"{BACKEND_URL}/movies")
        movies_data = movies_res.json() if movies_res.status_code == 200 else []
        
        if not movies_data:
            st.warning("먼저 영화를 등록해주세요.")
        else:
            movie_options = {f"{m['id']}. {m['title']}": m['id'] for m in movies_data}
            selected_movie_label = st.selectbox("리뷰할 영화 선택", list(movie_options.keys()))
            selected_movie_id = movie_options[selected_movie_label]

            st.subheader("리뷰 쓰기")
            with st.form("review_form"):
                user_name = st.text_input("작성자 이름")
                content = st.text_area("리뷰 내용 (AI가 감정을 분석합니다)")
                review_submit = st.form_submit_button("리뷰 등록")
                
                if review_submit:
                    new_review = {
                        "movie_id": selected_movie_id,
                        "user_name": user_name,
                        "content": content
                    }
                    res = requests.post(f"{BACKEND_URL}/reviews", json=new_review)
                    if res.status_code == 200:
                        result = res.json()
                        st.success("리뷰 등록 완료!")
                        st.info(f"🤖 AI 분석 결과: **{result['sentiment']}** ({result['score']}%)")
                    else:
                        st.error("리뷰 등록 실패")

            st.divider()
            st.subheader(f"'{selected_movie_label}'의 리뷰 목록")
            reviews_res = requests.get(f"{BACKEND_URL}/reviews/{selected_movie_id}")
            if reviews_res.status_code == 200:
                reviews = reviews_res.json()
                for rev in reviews:
                    with st.chat_message("user"):
                        st.write(f"**{rev['user_name']}**: {rev['content']}")
                        # 감정에 따른 색상 적용 (긍정: 파랑, 그 외: 빨강)
                        color = "blue" if rev['sentiment'] == "긍정" else "red"
                        st.markdown(f":{color}[AI 분석: {rev['sentiment']} ({rev['score']}%) ]")
    except Exception as e:
        st.error("서버 연결 확인 필요")