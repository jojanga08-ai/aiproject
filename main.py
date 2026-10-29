inport streamlit at
st.title('나의 첫 웹 서비스 만들기')
a=st.text_input('이름을 입력해주세요')
b=st.selectbox('좋아하는 음식을 선택하세요!',['훠궈','연어','샤오롱바오'])
if st.button('인사말 생성'):
  st.write('반갑습니다!')
  st.info(a+'제노야 안녕!')
  st.warning(b+'를 좋아하시네요!')
  st.error('잘 부탁드립니다!')
