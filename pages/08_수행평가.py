
import streamlit as st
import csv
from pathlib import Path
from collections import Counter

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="우리 동네 빵집 찾기",
    page_icon="🥐",
    layout="wide"
)

st.title("🥐 우리 동네 빵집 찾기")
st.subheader("🍞 전국의 빵집을 지도에서 찾아보자!")
st.write("지역을 선택하고 주변에 어떤 빵집이 있는지 확인해 봐요. 😊")

st.divider()


# ==========================================
# 2. CSV 파일 불러오기
# ==========================================

@st.cache_data
def load_data():

    # pages 폴더의 상위 폴더
    base_dir = Path(__file__).resolve().parent.parent

    csv_path = base_dir / "식품_제과점영업 111.csv"

    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV 파일을 찾을 수 없습니다.\n{csv_path}"
        )

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
    st.error("CSV 파일을 불러오지 못했어요.")
    st.code(str(e))
    st.stop()

if not data:
    st.warning("빵집 데이터가 없습니다.")
    st.stop()


# ==========================================
# 3. 지역별 대표 좌표
# ==========================================

# 개별 빵집 좌표가 아닌 시도별 대표 위치
REGION_COORDS = {

    "서울특별시": (37.5665, 126.9780),
    "부산광역시": (35.1796, 129.0756),
    "대구광역시": (35.8714, 128.6014),
    "인천광역시": (37.4563, 126.7052),
    "광주광역시": (35.1595, 126.8526),
    "대전광역시": (36.3504, 127.3845),
    "울산광역시": (35.5384, 129.3114),
    "세종특별자치시": (36.4800, 127.2890),

    "경기도": (37.4138, 127.5183),
    "강원도": (37.8228, 128.1555),
    "강원특별자치도": (37.8228, 128.1555),

    "충청북도": (36.6357, 127.4914),
    "충청남도": (36.5184, 126.8000),

    "전라북도": (35.7175, 127.1530),
    "전북특별자치도": (35.7175, 127.1530),
    "전라남도": (34.8679, 126.9910),

    "경상북도": (36.4919, 128.8889),
    "경상남도": (35.4606, 128.2132),

    "제주특별자치도": (33.4996, 126.5312)
}


# ==========================================
# 4. 주소 및 지역 정보 추출
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
    sigungu = parts[1]

    # 수원시 영통구처럼 시와 구가 함께 있는 경우
    if len(parts) >= 3 and parts[2].endswith("구"):
        sigungu = parts[1] + " " + parts[2]

    return sido, sigungu


# 모든 데이터에 지역 정보 추가

for row in data:

    address = get_address(row)

    sido, sigungu = get_region(address)

    row["_시도"] = sido
    row["_시군구"] = sigungu


# ==========================================
# 5. 전국 빵집 지역별 통계
# ==========================================

sido_counts = Counter()

sigungu_counts = Counter()

for row in data:

    sido = row["_시도"]
    sigungu = row["_시군구"]

    if sido:
        sido_counts[sido] += 1

    if sido and sigungu:
        sigungu_counts[(sido, sigungu)] += 1


# ==========================================
# 6. 지도 데이터 만들기
# ==========================================

map_points = []

for sido, count in sido_counts.items():

    if sido not in REGION_COORDS:
        continue

    lat, lon = REGION_COORDS[sido]

    map_points.append({
        "lat": lat,
        "lon": lon,
        "bakery_count": count
    })


# ==========================================
# 7. 전국 빵집 분포 지도
# ==========================================

st.header("🗺️ 전국 빵집 분포도")

st.write(
    "지도 위의 원이 클수록 해당 지역의 빵집이 많다는 뜻이에요!"
)

st.caption(
    "※ 각 마커는 시·도의 대표 좌표에 표시한 지역별 집계입니다. "
    "개별 빵집의 정확한 위치는 아닙니다."
)

if map_points:

    try:
        st.map(
            map_points,
            latitude="lat",
            longitude="lon",
            size="bakery_count",
            zoom=6,
            height=500
        )

    except Exception as e:
        st.warning("지도를 표시하지 못했어요.")
        st.code(str(e))

else:
    st.warning("지도에 표시할 지역 정보가 없습니다.")


# ==========================================
# 8. 전국 빵집 수 순위
# ==========================================

st.subheader("🏆 빵집이 많은 지역 TOP 10")

top_regions = sido_counts.most_common(10)

if top_regions:

    for rank, (region, count) in enumerate(top_regions, 1):

        st.write(
            f"**{rank}위 🥐 {region}** : {count:,}곳"
        )


# ==========================================
# 9. 지역 선택
# ==========================================

st.divider()

st.header("📍 우리 동네 빵집 찾기")

sido_list = sorted(
    set(
        row["_시도"]
        for row in data
        if row["_시도"]
    )
)

if not sido_list:
    st.error("주소에서 지역을 찾을 수 없습니다.")
    st.stop()


selected_sido = st.selectbox(
    "① 시·도 선택",
    sido_list
)


sido_data = [
    row for row in data
    if row["_시도"] == selected_sido
]


sigungu_list = sorted(
    set(
        row["_시군구"]
        for row in sido_data
        if row["_시군구"]
    )
)


selected_sigungu = st.selectbox(
    "② 시·군·구 선택",
    ["전체 지역"] + sigungu_list
)


# ==========================================
# 10. 선택 지역 빵집 검색
# ==========================================

if selected_sigungu == "전체 지역":

    filtered_data = sido_data

else:

    filtered_data = [
        row for row in sido_data
        if row["_시군구"] == selected_sigungu
    ]


# 이름 검색
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
# 11. 검색 결과 통계
# ==========================================

st.divider()

st.header("🎂 검색 결과")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "검색된 빵집",
        f"{len(filtered_data):,}곳"
    )

with col2:

    st.metric(
        "선택한 지역",
        selected_sigungu
        if selected_sigungu != "전체 지역"
        else selected_sido
    )


# ==========================================
# 12. 방문자수 확인
# ==========================================

def get_visitor_count(row):

    columns = [
        "방문자수",
        "방문자 수",
        "방문자수(명)",
        "방문객수"
    ]

    for column in columns:

        value = (row.get(column) or "").strip()

        if value:

            try:
                return int(value.replace(",", ""))

            except ValueError:
                pass

    return None


has_visitor_data = (
    bool(filtered_data)
    and all(
        get_visitor_count(row) is not None
        for row in filtered_data
    )
)


if has_visitor_data:

    filtered_data.sort(
        key=get_visitor_count,
        reverse=True
    )

    st.success("🏆 방문자수 기준 인기순 정렬!")

else:

    filtered_data.sort(
        key=lambda row: row.get("사업장명") or ""
    )

    st.info(
        "💡 현재 CSV에는 실제 방문자수 정보가 없어요. "
        "빵집 이름순으로 표시합니다."
    )


# ==========================================
# 13. 빵집 목록 출력
# ==========================================

if not filtered_data:

    st.warning("검색된 빵집이 없습니다.")

else:

    for index, row in enumerate(filtered_data):

        name = row.get("사업장명") or "이름 없음"

        road = (row.get("도로명주소") or "").strip()

        jibun = (row.get("지번주소") or "").strip()

        homepage = (row.get("홈페이지") or "").strip()

        address = road if road else jibun

        visitor_count = get_visitor_count(row)

        with st.container(border=True):

            if has_visitor_data:

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
                f"📍 주소: {address or '주소 정보 없음'}"
            )

            if road and jibun:
                st.caption(f"지번주소: {jibun}")

            if homepage:

                if homepage.startswith(("http://", "https://")):

                    st.markdown(
                        f"🌐 [홈페이지 바로가기]({homepage})"
                    )

                else:

                    st.write(f"🌐 홈페이지: {homepage}")


# ==========================================
# 14. 마무리
# ==========================================

st.divider()

st.markdown(
    """
    ### 🍰 오늘은 어떤 빵을 먹을까?

    🥐 전국에는 정말 다양한 빵집이 있어요!

    📍 지도를 통해 빵집이 많은 지역을 찾아보고

    🍞 새로운 빵집도 발견해 보세요!

    💛 맛있는 빵과 함께 즐거운 하루 보내세요!
    """
)

st.caption(
    "자료 출처: 제공된 식품_제과점영업 CSV"
)
