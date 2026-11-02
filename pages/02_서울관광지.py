
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# =====================================
# 1. 페이지 제목
# =====================================

st.title("🇰🇷 서울 인기 관광지 TOP 10")
st.subheader("외국인 관광객을 위한 서울 여행 가이드")

st.markdown("""
서울을 방문하는 외국인 관광객에게 추천하는
대표 관광지 10곳을 지도에서 확인해 보세요! 🗺️
""")

# =====================================
# 2. 관광지 데이터
# =====================================

SPOTS = [
    {
        "rank": 1,
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "category": "역사·문화",
        "description": "조선 왕조의 대표 궁궐입니다. 아름다운 전통 건축과 한국의 역사를 경험할 수 있습니다.",
        "tip": "한복을 입고 방문하면 특별한 사진을 남길 수 있습니다."
    },
    {
        "rank": 2,
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "category": "전망·야경",
        "description": "남산에 위치한 서울의 대표 랜드마크입니다. 서울의 아름다운 야경을 감상할 수 있습니다.",
        "tip": "해 질 무렵 방문하는 것을 추천합니다."
    },
    {
        "rank": 3,
        "name": "명동",
        "english": "Myeongdong",
        "lat": 37.5636,
        "lon": 126.9869,
        "category": "쇼핑·먹거리",
        "description": "한국 화장품과 패션 쇼핑, 다양한 길거리 음식으로 유명한 관광지입니다.",
        "tip": "저녁 시간에 방문하면 다양한 길거리 음식을 즐길 수 있습니다."
    },
    {
        "rank": 4,
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "category": "전통·문화",
        "description": "전통 한옥이 모여 있는 아름다운 마을입니다. 한국의 옛 주거 문화를 경험할 수 있습니다.",
        "tip": "주민들이 실제 거주하는 곳이므로 조용히 관람해 주세요."
    },
    {
        "rank": 5,
        "name": "창덕궁",
        "english": "Changdeokgung Palace",
        "lat": 37.5794,
        "lon": 126.9910,
        "category": "역사·문화",
        "description": "유네스코 세계문화유산으로 지정된 궁궐입니다. 아름다운 후원으로 유명합니다.",
        "tip": "후원 관람은 사전 예약 여부를 확인하세요."
    },
    {
        "rank": 6,
        "name": "홍대 거리",
        "english": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "category": "문화·엔터테인먼트",
        "description": "거리 공연, 음악, 개성 있는 카페와 쇼핑을 즐길 수 있는 젊음의 거리입니다.",
        "tip": "주말에 방문하면 다양한 거리 공연을 볼 수 있습니다."
    },
    {
        "rank": 7,
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700,
        "lon": 126.9998,
        "category": "전통시장·먹거리",
        "description": "빈대떡, 마약김밥, 만두 등 한국의 다양한 전통 음식을 맛볼 수 있습니다.",
        "tip": "한국 전통시장의 활기찬 분위기를 경험해 보세요."
    },
    {
        "rank": 8,
        "name": "동대문디자인플라자",
        "english": "Dongdaemun Design Plaza",
        "lat": 37.5665,
        "lon": 127.0092,
        "category": "건축·전시",
        "description": "독특한 곡선형 건축 디자인이 인상적인 복합문화공간입니다.",
        "tip": "야간 조명이 켜진 건물 외관도 감상해 보세요."
    },
    {
        "rank": 9,
        "name": "청계천",
        "english": "Cheonggyecheon Stream",
        "lat": 37.5693,
        "lon": 126.9827,
        "category": "산책·자연",
        "description": "서울 도심 한가운데 흐르는 아름다운 하천입니다. 산책과 휴식을 즐기기 좋습니다.",
        "tip": "주변 광장과 연결해서 산책해 보세요."
    },
    {
        "rank": 10,
        "name": "롯데월드타워·서울스카이",
        "english": "Lotte World Tower & Seoul Sky",
        "lat": 37.5125,
        "lon": 127.1025,
        "category": "전망·랜드마크",
        "description": "서울의 대표적인 초고층 건물입니다. 전망대에서 서울의 전경을 감상할 수 있습니다.",
        "tip": "전망대 입장 시간과 예약 정보를 미리 확인하세요."
    }
]

# =====================================
# 3. 사이드바 필터
# =====================================

st.sidebar.header("🗺️ 관광지 설정")

categories = sorted(
    list(set(spot["category"] for spot in SPOTS))
)

selected_categories = st.sidebar.multiselect(
    "관광지 종류 선택",
    categories,
    default=categories
)

show_names = st.sidebar.checkbox(
    "지도에 관광지 이름 표시",
    value=True
)

visible_spots = [
    spot for spot in SPOTS
    if spot["category"] in selected_categories
]

# =====================================
# 4. 서울 지도 생성
# =====================================

m = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="OpenStreetMap",
    control_scale=True
)

# 마커 클러스터
marker_cluster = MarkerCluster().add_to(m)

# =====================================
# 5. 지도에 관광지 표시
# =====================================

for spot in visible_spots:

    popup_html = f"""
    <div style="width:230px;">
        <h3>TOP {spot['rank']}. {spot['name']}</h3>
        <b>{spot['english']}</b>
        <hr>
        <p>{spot['description']}</p>
        <p>💡 {spot['tip']}</p>
    </div>
    """

    marker_label = (
        f"TOP {spot['rank']} - {spot['name']}"
        if show_names
        else f"TOP {spot['rank']}"
    )

    folium.Marker(
        location=[
            spot["lat"],
            spot["lon"]
        ],
        tooltip=marker_label,
        popup=folium.Popup(
            popup_html,
            max_width=300
        ),
        icon=folium.DivIcon(
            html=f"""
            <div style="
                background-color:#e53935;
                color:white;
                border:2px solid white;
                border-radius:50%;
                width:32px;
                height:32px;
                text-align:center;
                line-height:28px;
                font-weight:bold;
                font-size:14px;
                box-shadow:0 2px 5px rgba(0,0,0,0.4);
            ">
                {spot['rank']}
            </div>
            """,
            icon_size=(32, 32),
            icon_anchor=(16, 16)
        )
    ).add_to(marker_cluster)

# =====================================
# 6. 지도 화면 출력
# =====================================

st.markdown("---")
st.header("📍 서울 주요 관광지 지도")

if visible_spots:

    st_folium(
        m,
        use_container_width=True,
        height=600,
        returned_objects=[]
    )

else:
    st.warning("표시할 관광지를 선택해 주세요.")

# =====================================
# 7. 관광지 설명
# =====================================

st.markdown("---")
st.header("✨ 서울 관광지 TOP 10 소개")

st.write(
    "각 관광지의 특징과 방문 팁을 확인해 보세요!"
)

# 2열 카드 형식
for start in range(0, len(visible_spots), 2):

    cols = st.columns(2)

    for col, spot in zip(
        cols,
        visible_spots[start:start + 2]
    ):

        with col:

            with st.container(border=True):

                st.subheader(
                    f"{spot['rank']}. {spot['name']}"
                )

                st.caption(
                    f"{spot['english']} | {spot['category']}"
                )

                st.write(
                    spot["description"]
                )

                st.info(
                    f"💡 방문 팁: {spot['tip']}"
                )

                google_map_url = (
                    "https://www.google.com/maps/search/?api=1"
                    f"&query={spot['lat']},{spot['lon']}"
                )

                st.link_button(
                    "📍 Google 지도에서 위치 확인",
                    google_map_url
                )

# =====================================
# 8. 하단 안내
# =====================================

st.markdown("---")

st.success(
    "즐거운 서울 여행 되세요! 🇰🇷"
)

st.caption(
    "관광지 목록은 공식 실시간 방문객 순위가 아닌 "
    "서울 대표 명소를 소개하기 위한 선정 목록입니다."
)

st.caption(
    "지도 데이터: OpenStreetMap"
)
