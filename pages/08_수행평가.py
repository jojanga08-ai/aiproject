
import streamlit as st
import csv
from pathlib import Path

# =====================================
# 1. 페이지 설정
# =====================================

st.set_page_config(
    page_title="우리 동네 빵집 찾기",
    page_icon="🥐",
    layout="wide"
)

st.title("🥐 우리 동네 빵집 찾기")
st.subheader("🍞 내가 사는 지역에는 어떤 빵집이 있을까?")
st.write("지역을 선택하고 우리 동네의 다양한 빵집을 찾아보세요!")

st.divider()


# =====================================
# 2. CSV 파일 불러오기
# =====================================

@st.cache_data
def load_data():

    file_path = Path(__file__).parent / "식품_제과점영업 111.csv"

    if not file_path.exists():
        return None

    # 한글 인코딩 자동 대응
    for encoding in ["utf-8-sig", "cp949", "euc-kr"]:

        try:
            with open(
                file_path,
                "r",
                encoding=encoding,
                newline=""
            ) as file:

                reader = csv.DictReader(file)
                data = list(reader)

            return data

        except UnicodeDecodeError:
            continue

    return None


data = load_data()

if data is None:
    st.error("CSV 파일을 찾을 수 없거나 인코딩을 확인할 수 없습니다.")
    st.stop()

if not data:
    st.warning("등록된 빵집 데이터가 없습니다.")
    st.stop()


# =====================================
# 3. 주소 정보 정리
# =====================================

def get_address(row):

    address = (
        row.get("도로명주소")
        or row.get("지번주소")
        or ""
    ).strip()

    return address


def get_region(address):

    parts = address.split()

    if len(parts) >= 2:
        return parts[0], parts[1]

    return "기타", "기타"


for row in data:

    address = get_address(row)

    sido, sigungu = get_region(address)

    row["_시도"] = sido
    row["_시군구"] = sigungu


# =====================================
# 4. 지역 선택
# =====================================

st.subheader("📍 어디에 있는 빵집을 찾을까요?")

sido_list = sorted(set(
    row["_시도"] for row in data
))

selected_sido = st.selectbox(
    "시·도 선택",
    sido_list
)

filtered_data = [
    row for row in data
    if row["_시도"] == selected_sido
]

sigungu_list = sorted(set(
    row["_시군구"] for row in filtered_data
))

selected_sigungu = st.selectbox(
    "시·군·구 선택",
    ["전체"] + sigungu_list
)

if selected_sigungu != "전체":

    filtered_data = [
        row for row in filtered_data
        if row["_시군구"] == selected_sigungu
    ]


# =====================================
# 5. 방문자수 확인 및 인기순 정렬
# =====================================

def get_visitor_count(row):

    value = (
        row.get("방문자수")
        or row.get("방문자 수")
        or ""
    ).strip()

    try:
        return int(value.replace(",", ""))
    except (ValueError, AttributeError):
        return -1


has_visitor_data = (
    len(filtered_data) > 0
    and all(get_visitor_count(row) >= 0 for row in filtered_data)
)


if has_visitor_data:

    filtered_data.sort(
        key=get_visitor_count,
        reverse=True
    )

else:

    filtered_data.sort(
        key=lambda row: row.get("사업장명", "")
    )


# =====================================
# 6. 검색 결과
# =====================================

st.divider()

st.subheader("🎂 우리 지역 빵집 목록")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "검색된 빵집",
        f"{len(filtered_data):,}곳"
    )

with col2:
    st.metric(
        "선택한 지역",
        selected_sido
    )

if has_visitor_data:

    st.success("방문자수 기준으로 인기순 정렬했어요! 🏆")

else:

    st.info(
        "💡 현재 데이터에는 방문자수가 없어요. "
        "실제 인기순 정렬을 위해서는 방문자수 자료가 필요해요. "
        "현재는 빵집 이름순으로 보여드릴게요."
    )


# =====================================
# 7. 빵집 정보 출력
# =====================================

if not filtered_data:

    st.warning("선택한 지역에는 검색된 빵집이 없어요.")

else:

    for index, row in enumerate(filtered_data):

        name = row.get("사업장명", "이름 없음")
        road = row.get("도로명주소", "")
        jibun = row.get("지번주소", "")
        homepage = row.get("홈페이지", "")

        with st.container(border=True):

            if has_visitor_data:

                st.markdown(
                    f"### 🏆 {index + 1}위 | {name}"
                )

                st.write(
                    f"👣 방문자수: {get_visitor_count(row):,}명"
                )

            else:

                st.markdown(
                    f"### 🥐 {index + 1}. {name}"
                )

            st.write(f"📍 주소: {road or jibun or '주소 정보 없음'}")

            if road and jibun:
                st.caption(f"지번주소: {jibun}")

            if homepage:
                st.write(f"🌐 홈페이지: {homepage}")


# =====================================
# 8. 마무리 안내
# =====================================

st.divider()

st.markdown(
    """
    ### 🍰 오늘은 어떤 빵을 먹어볼까요?

    우리 동네에도 맛있는 빵집이 숨어 있을지 몰라요!

    친구들과 함께 새로운 빵집을 찾아보세요. 😊
    """
)

