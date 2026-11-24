
import streamlit as st
import csv
from pathlib import Path

# ==========================================
# 1. 페이지 기본 설정
# ==========================================

st.set_page_config(
    page_title="우리 동네 빵집 찾기",
    page_icon="🥐",
    layout="wide"
)

st.title("🥐 우리 동네 빵집 찾기")
st.subheader("🍞 지역을 선택하고 맛있는 빵집을 찾아보세요!")
st.write("우리 동네에는 어떤 빵집이 있을까요? 함께 찾아봐요! 😊")

st.divider()


# ==========================================
# 2. CSV 파일 불러오기
# ==========================================

@st.cache_data
def load_data():

    # pages 폴더의 상위 폴더
    base_dir = Path(__file__).resolve().parent.parent

    # CSV 파일 경로
    csv_path = base_dir / "식품_제과점영업 111.csv"

    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV 파일을 찾을 수 없습니다: {csv_path}"
        )

    # CP949 인코딩으로 읽기
    with open(
        csv_path,
        "r",
        encoding="cp949",
        newline=""
    ) as file:

        reader = csv.DictReader(file)
        data = list(reader)

    return data


try:
    data = load_data()

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했어요.")
    st.code(str(e))
    st.stop()


if not data:
    st.warning("빵집 데이터가 없습니다.")
    st.stop()


# ==========================================
# 3. 주소 정리
# ==========================================

def get_address(row):

    road = (row.get("도로명주소") or "").strip()
    jibun = (row.get("지번주소") or "").strip()

    return road if road else jibun


def get_region(address):

    parts = address.split()

    if len(parts) < 2:
        return None, None

    sido = parts[0]

    # 시/군/구 단위 지역 구분
    sigungu = parts[1]

    # 경기도 수원시 영통구처럼
    # 시 다음에 구가 있는 경우
    if len(parts) >= 3 and parts[2].endswith("구"):
        sigungu = parts[1] + " " + parts[2]

    return sido, sigungu


# 주소 정보 추가
for row in data:

    address = get_address(row)

    sido, sigungu = get_region(address)

    row["_시도"] = sido
    row["_시군구"] = sigungu


# ==========================================
# 4. 지역 선택
# ==========================================

st.header("📍 지역 선택하기")

sido_list = sorted(set(
    row["_시도"]
    for row in data
    if row["_시도"]
))

if not sido_list:
    st.error("지역 주소를 확인할 수 없습니다.")
    st.stop()

selected_sido = st.selectbox(
    "① 시·도 선택",
    sido_list
)

# 선택한 시도에 해당하는 데이터
sido_data = [
    row for row in data
    if row["_시도"] == selected_sido
]

sigungu_list = sorted(set(
    row["_시군구"]
    for row in sido_data
    if row["_시군구"]
))

selected_sigungu = st.selectbox(
    "② 시·군·구 선택",
    ["전체 지역"] + sigungu_list
)


# ==========================================
# 5. 빵집 검색
# ==========================================

if selected_sigungu == "전체 지역":

    filtered_data = sido_data

else:

    filtered_data = [
        row for row in sido_data
        if row["_시군구"] == selected_sigungu
    ]


st.divider()

search_word = st.text_input(
    "🔎 빵집 이름 검색",
    placeholder="예: 파리바게뜨, 뚜레쥬르"
)

if search_word:

    filtered_data = [
        row for row in filtered_data
        if search_word.lower()
        in (row.get("사업장명") or "").lower()
    ]


# ==========================================
# 6. 방문자수 데이터 확인
# ==========================================

def get_visitor_count(row):

    # 방문자수 열이 추가된 경우에도 사용할 수 있도록 설정
    possible_columns = [
        "방문자수",
        "방문자 수",
        "방문자수(명)",
        "방문객수"
    ]

    for column in possible_columns:

        value = (row.get(column) or "").strip()

        if value:

            try:
                return int(
                    value.replace(",", "")
                )
            except ValueError:
                continue

    return None


has_visitor_data = any(
    get_visitor_count(row) is not None
    for row in filtered_data
)


# 방문자수 데이터가 있다면 인기순 정렬
if has_visitor_data:

    filtered_data.sort(
        key=lambda row: (
            get_visitor_count(row) is None,
            -(get_visitor_count(row) or 0)
        )
    )

else:

    # 방문자수 데이터가 없다면 이름순 정렬
    filtered_data.sort(
        key=lambda row: row.get("사업장명") or ""
    )


# ==========================================
# 7. 검색 결과 요약
# ==========================================

st.header("🥐 우리 지역 빵집")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        label="검색된 빵집",
        value=f"{len(filtered_data):,}곳"
    )

with col2:

    st.metric(
        label="선택한 지역",
        value=selected_sigungu
        if selected_sigungu != "전체 지역"
        else selected_sido
    )


# ==========================================
# 8. 인기순 안내
# ==========================================

if has_visitor_data:

    st.success(
        "🏆 방문자수 기준으로 인기순 정렬했어요!"
    )

else:

    st.info(
        "💡 현재 CSV에는 실제 방문자수 정보가 없어요. "
        "빵집 이름순으로 정렬해서 보여드릴게요!"
    )


# ==========================================
# 9. 빵집 목록 출력
# ==========================================

if len(filtered_data) == 0:

    st.warning(
        "앗! 검색 결과가 없어요. 다른 지역이나 이름을 검색해 보세요."
    )

else:

    for index, row in enumerate(filtered_data):

        name = row.get("사업장명") or "이름 정보 없음"

        road = (row.get("도로명주소") or "").strip()

        jibun = (row.get("지번주소") or "").strip()

        homepage = (row.get("홈페이지") or "").strip()

        address = road if road else jibun

        visitor_count = get_visitor_count(row)

        with st.container(border=True):

            if visitor_count is not None:

                st.markdown(
                    f"### 🏆 {index + 1}위 | {name}"
                )

                st.write(
                    f"👣 방문자수: {visitor_count:,}명"
                )

            else:

                st.markdown(
                    f"### 🥐 {index + 1}. {name}"
                )

            st.write(
                f"📍 주소: {address if address else '주소 정보 없음'}"
            )

            if road and jibun:

                st.caption(
                    f"지번주소: {jibun}"
                )

            if homepage:

                if homepage.startswith(("http://", "https://")):

                    st.markdown(
                        f"🌐 [홈페이지 바로가기]({homepage})"
                    )

                else:

                    st.write(
                        f"🌐 홈페이지: {homepage}"
                    )


# ==========================================
# 10. 마무리
# ==========================================

st.divider()

st.markdown(
    """
    ### 🍰 오늘은 빵 먹는 날!

    🥐 우리 동네의 새로운 빵집을 발견해 보세요!

    🍞 친구들과 함께 맛있는 빵을 찾아 떠나봐요!

    💛 빵은 언제 먹어도 행복하니까요!
    """
)

st.caption(
    "데이터 출처: 제공된 식품_제과점영업 CSV 파일"
)
