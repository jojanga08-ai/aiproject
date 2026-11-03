
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="세계 국가별 MBTI 분석",
    page_icon="🌏",
    layout="wide"
)

st.title("🌏 세계 국가별 MBTI 분석")
st.markdown("국가를 선택하면 해당 국가의 MBTI 16가지 유형별 비율을 확인할 수 있습니다.")

# ==========================================
# 2. CSV 데이터 불러오기
# ==========================================
CSV_FILE = Path(__file__).parent / "countriesMBTI_16types (1).csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_FILE)

    df.columns = df.columns.str.strip()
    df["Country"] = df["Country"].astype(str).str.strip()

    mbti_columns = [
        "ISTJ", "ISFJ", "INFJ", "INTJ",
        "ISTP", "ISFP", "INFP", "INTP",
        "ESTP", "ESFP", "ENFP", "ENTP",
        "ESTJ", "ESFJ", "ENFJ", "ENTJ"
    ]

    for col in mbti_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df[mbti_columns] = df[mbti_columns].fillna(0)

    return df, mbti_columns


try:
    df, mbti_columns = load_data()
except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다. app.py와 같은 폴더에 CSV 파일을 넣어주세요.")
    st.stop()
except Exception as e:
    st.error(f"데이터를 불러올 수 없습니다: {e}")
    st.stop()


# ==========================================
# 3. 국가 선택
# ==========================================
countries = sorted(df["Country"].unique())

default_index = (
    countries.index("South Korea")
    if "South Korea" in countries
    else 0
)

selected_country = st.selectbox(
    "🗺️ 국가를 선택하세요",
    countries,
    index=default_index
)


# ==========================================
# 4. 선택한 국가 데이터 가져오기
# ==========================================
country_data = df[
    df["Country"] == selected_country
][mbti_columns].iloc[0]

# 데이터가 0~1 사이이면 백분율로 변환
if country_data.max() <= 1:
    percentages = country_data * 100
else:
    percentages = country_data.copy()


# ==========================================
# 5. MBTI 비율 순위 정렬
# ==========================================
chart_data = pd.DataFrame({
    "MBTI": percentages.index,
    "비율": percentages.values
})

chart_data = chart_data.sort_values(
    by="비율",
    ascending=False
).reset_index(drop=True)


# ==========================================
# 6. 상단 주요 통계
# ==========================================
top_type = chart_data.iloc[0]["MBTI"]
top_value = chart_data.iloc[0]["비율"]

second_type = chart_data.iloc[1]["MBTI"]
second_value = chart_data.iloc[1]["비율"]

col1, col2, col3 = st.columns(3)

col1.metric(
    "🌍 선택한 국가",
    selected_country
)

col2.metric(
    "🥇 MBTI 1위",
    top_type,
    f"{top_value:.2f}%"
)

col3.metric(
    "🥈 MBTI 2위",
    second_type,
    f"{second_value:.2f}%"
)

st.divider()


# ==========================================
# 7. 그라데이션 색상 만들기
# ==========================================
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")

    return tuple(
        int(hex_color[i:i+2], 16)
        for i in (0, 2, 4)
    )


def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def interpolate_color(start, end, amount):
    start_rgb = hex_to_rgb(start)
    end_rgb = hex_to_rgb(end)

    rgb = tuple(
        round(
            start_rgb[i] +
            (end_rgb[i] - start_rgb[i]) * amount
        )
        for i in range(3)
    )

    return rgb_to_hex(rgb)


# 1위는 쨍한 연두색
# 순위가 내려갈수록 연한 연두색
colors = [
    interpolate_color(
        "#7CFC00",
        "#EFF9D8",
        i / max(len(chart_data) - 1, 1)
    )
    for i in range(len(chart_data))
]


# ==========================================
# 8. 막대그래프 만들기
# ==========================================
fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=chart_data["비율"],
        y=chart_data["MBTI"],
        orientation="h",

        marker=dict(
            color=colors,
            line=dict(
                color="white",
                width=0.8
            )
        ),

        text=[
            f"{v:.2f}%"
            for v in chart_data["비율"]
        ],

        textposition="outside",

        hovertemplate=
        "<b>%{y}</b><br>" +
        "비율: %{x:.2f}%" +
        "<extra></extra>"
    )
)


# ==========================================
# 9. 그래프 디자인
# ==========================================
fig.update_layout(

    title={
        "text": f"📊 {selected_country}의 MBTI 유형별 비율",
        "x": 0.02
    },

    xaxis=dict(
        title="MBTI 비율 (%)",
        rangemode="tozero",
        showgrid=True,
        gridcolor="rgba(120,120,120,0.15)",
        ticksuffix="%"
    ),

    yaxis=dict(
        title="MBTI 유형",
        autorange="reversed"
    ),

    height=650,

    margin=dict(
        l=30,
        r=75,
        t=80,
        b=50
    ),

    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",

    font=dict(size=14),

    showlegend=False
)


# ==========================================
# 10. Streamlit 화면에 그래프 출력
# ==========================================
st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 11. MBTI 순위표
# ==========================================
with st.expander("📋 MBTI 비율 순위표 보기"):

    display_data = chart_data.copy()

    display_data.insert(
        0,
        "순위",
        range(1, len(display_data) + 1)
    )

    display_data["비율"] = display_data["비율"].apply(
        lambda x: f"{x:.2f}%"
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 12. 안내 문구
# ==========================================
st.info(
    "참고: 이 앱은 제공된 CSV 데이터의 값을 시각화합니다. "
    "실제 국가별 인구의 MBTI 분포와 차이가 있을 수 있습니다."
)

st.caption("🌱 World MBTI Explorer | Made with Streamlit")
