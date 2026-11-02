
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# 페이지 설정
st.set_page_config(
    page_title="서울 인기 관광지 TOP 10",
    page_icon="🇰🇷",
    layout="wide"
)

# 서울 관광지 데이터
SPOTS = [
    {
        "rank": 1,
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "category": "역사·문화",
        "description": "조선 왕조의 대표 궁궐로, 근정전과 경회루 등 아름다운 전통 건축을 만날 수 있어요.",
        "tip": "한복을 입고 방문하면 특별한 사진을 남기기 좋아요."
    },
    {
        "rank": 2,
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "category": "전망·야경",
        "description": "남산 정상 부근에서 서울의 도심 풍경과 야경을 한눈에 감상할 수 있는 전망 명소예요.",
        "tip": "해 질 무렵 올라가면 낮과 밤의 풍경을 모두 볼 수 있어요."
    },
    {
        "rank": 3,
        "name": "명동",
        "english": "Myeongdong",
        "lat": 37.5636,
        "lon": 126.9869,
        "category": "쇼핑·먹거리",
        "description": "화장품 쇼핑과 길거리 음식으로 유명한 번화가예요. 다양한 먹거리와 상점을 둘러보세요.",
        "tip": "저녁 시간에는 길거리 음식 매장이 활기를 띠어요."
    },
    {
        "rank": 4,
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "category": "전통·골목",
        "description": "전통 한옥이 모여 있는 마을로, 서울의 옛 주거 풍경과 골목길을 느낄 수 있어요.",
        "tip": "실제 주민이 거주하는 곳이므로 조용히 관람하고 안내 표지를 따라주세요."
    },
    {
        "rank": 5,
        "name": "창덕궁",
        "english": "Changdeokgung Palace",
        "lat": 37.5794,
        "lon": 126.9910,
        "category": "역사·문화",
        "description": "자연 지형을 살려 지은 궁궐로, 아름다운 정원인 후원으로도 잘 알려져 있어요.",
        "tip": "후원 관람은 운영 시간과 예약 여부를 미리 확인하세요."
    },
    {
        "rank": 6,
        "name": "홍대 거리",
        "english": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "category": "문화·엔터테인먼트",
        "description": "젊은 문화와 인디 음악, 거리 공연, 개성 있는 카페와 상점이 모인 활기찬 지역이에요.",
        "tip": "주말에는 거리 공연과 다양한 팝업 행사를 만날 수 있어요."
    },
    {
        "rank": 7,
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700,
        "lon": 126.9998,
        "category": "전통시장·먹거리",
        "description": "빈대떡, 김밥, 만두 등 한국 시장 음식을 맛보고 활기찬 시장 분위기를 경험할 수 있어요.",
        "tip": "점심시간에는 붐빌 수 있으니 여유 있게 방문해 보세요."
    },
    {
        "rank": 8,
        "name": "동대문디자인플라자(DDP)",
        "english": "Dongdaemun Design Plaza",
        "lat": 37.5665,
        "lon": 127.0092,
        "category": "건축·전시",
        "description": "독특한 곡선형 건축물이 인상적인 복합문화공간으로 전시와 디자인 행사가 열려요.",
        "tip": "건물 외관과 주변 조명은 저녁에도 사진 찍기 좋아요."
    },
    {
        "rank": 9,
        "name": "청계천",
        "english": "Cheonggyecheon Stream",
        "lat": 37.5693,
        "lon": 126.9827,
        "category": "산책·도심",
        "description": "도심 한가운데 흐르는 산책로로, 주변 명소를 둘러보며 잠시 쉬어가기 좋아요.",
        "tip": "주변 광장과 연결해 도보 코스로 즐겨보세요."
    },
    {
        "rank": 10,
        "name": "롯데월드타워·서울스카이",
        "english": "Lotte World Tower & Seoul Sky",
        "lat": 37.5125,
        "lon": 127.1025,
        "category": "전망·랜드마크",
        "description": "서울의 대표적인 초고층 랜드마크로, 전망대에서 넓은 서울 풍경을 감상할 수 있어요.",
        "tip": "전망대 이용 전 운영 시간과 입장권 정보를 확인하세요."
    }
]

# 제목
st.title("🇰🇷 외국인 관광객이 좋아하는 서울 관광지 TOP 10")

st.caption(
    "서울 여행을 계획할 때 참고할 수 있는 대표 관광지 지도입니다."
)

# 사이드바 설정
with st.sidebar:
    st.header("🗺️ 지도 설정")

    show_names = st.checkbox(
        "지도에 관광지 이름 표시",
        value=True
    )

    categories = sorted(
        {spot["category"] for spot in SPOTS}
    )

    selected_categories = st.multiselect(
        "관광지 유형 선택",
        options=categories,
        default=categories
    )

    st.markdown("---")
    st.info("지도 마커를 클릭하면 관광지 정보를 확인할 수 있어요!")

# 선택한 관광지만 표시
visible_spots = [
    spot for spot in SPOTS
    if spot["category"] in selected_categories
]

# 서울 지도 만들기
m = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="OpenStreetMap",
    control_scale=True
)

# 마커 클러스터
cluster = MarkerCluster().add_to(m)

# 관광지 마커 표시
for spot in visible_spots:

    popup_html = f"""
    <div style="width:220px">
        <h4>TOP {spot['rank']}. {spot['name']}</h4>
        <p>{spot['english']}</p>
        <p>{spot['description']}</p>
    </div>
    """

    label = (
        f"TOP {spot['rank']} · {spot['name']}"
        if show_names
        else f"TOP {spot['rank']}"
    )

    folium.Marker(
        location=[spot["lat"], spot["lon"]],
        tooltip=label,
        popup=folium.Popup(
            popup_html,
            max_width=280
        ),
        icon=folium.DivIcon(
            html=f"""
            <div style="
                background:#e53935;
                color:white;
                border:2px solid white;
                border-radius:50%;
                width:30px;
                height:30px;
                text-align:center;
                line-height:26px;
                font-weight:bold;
                box-shadow:0 1px 5px rgba(0,0,0,.45);
            ">
                {spot['rank']}
            </div>
            """,
            icon_size=(30, 30),
            icon_anchor=(15, 15)
        )
    ).add_to(cluster)

# 지도 표시
st.subheader("📍 서울 주요 관광지 지도")

st_folium(
    m,
    use_container_width=True,
    height=580,
    returned_objects=[]
)

# 관광지 설명
st.subheader("✨ 서울 관광지 TOP 10 소개")

st.write(
    "각 관광지의 특징과 방문 팁을 확인해 보세요!"
)

# 2열로 관광지 소개
for start in range(0, len(visible_spots), 2):

    cols = st.columns(2)

    for col, spot in zip(
        cols,
        visible_spots[start:start + 2]
    ):

        with col:

            with st.container(border=True):

                st.markdown(
                    f"### {spot['rank']}. {spot['name']}"
                )

                st.caption(
                    f"{spot['english']} · {spot['category']}"
                )

                st.write(spot["description"])

                st.info(
                    f"💡 방문 팁: {spot['tip']}"
                )

                map_url = (
                    "https://www.google.com/maps/search/?api=1"
                    f"&query={spot['lat']},{spot['lon']}"
                )

                st.link_button(
                    "Google 지도에서 위치 보기",
                    map_url
                )

# 하단 안내
st.markdown("---")

st.caption(
    "※ 관광지 순위는 공식 실시간 방문객 순위가 아닌 "
    "대표 명소 소개용 선정 목록입니다."
)

st.caption(
    "지도 데이터: OpenStreetMap"
)
