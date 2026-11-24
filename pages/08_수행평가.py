
import streamlit as st
import csv
from pathlib import Path

@st.cache_data
def load_data():

    # 현재 py 파일의 위치
    current_folder = Path(__file__).resolve().parent

    # CSV 파일이 있을 만한 위치
    possible_paths = [
        current_folder.parent / "식품_제과점영업 111.csv",
        current_folder / "식품_제과점영업 111.csv"
    ]

    # 파일 찾기
    file_path = None

    for path in possible_paths:
        if path.exists():
            file_path = path
            break

    if file_path is None:
        st.error("CSV 파일을 찾을 수 없습니다.")
        st.write("확인한 위치:")
        for path in possible_paths:
            st.code(str(path))
        return None

    # CP949 인코딩으로 읽기
    try:
        with open(
            file_path,
            "r",
            encoding="cp949",
            newline=""
        ) as file:

            reader = csv.DictReader(file)
            data = list(reader)

        return data

    except Exception as e:
        st.error(f"CSV 읽기 오류: {e}")
        return None


data = load_data()

if data is None:
    st.stop()

if len(data) == 0:
    st.warning("빵집 데이터가 없습니다.")
    st.stop()
