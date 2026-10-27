import streamlit as at
st.title('나의 첫 웹 서비스 만들기')
st.text_input('이름을 입력해주세요')
st.selectbox('좋아하는 음식을 선택하세요!',['훠궈','연어','샤오롱바오'])
st.button('인사말 생성')
