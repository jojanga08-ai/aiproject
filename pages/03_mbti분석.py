
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
st.markdown(
    "국가를 선택하면 해당 국가의 MBTI 16가지 유형별 비율을 확인할 수 있습니다."
)

# ==========================================
# 2. CSV 파일 경로 설정
# ==========================================
# 현재 파일은 pages 폴더 안에 있으므로
# parent.parent를 사용하면 프로젝트 상위 폴더로 이동합니다.

BASE_DIR = Path(__file__).resolve().parent.parent

CSV_FILE = BASE_DIR / "countriesMBTI_16types (1).csv"


# ==========================================
# 3. 데이터 불러오기
# ==========================================
@st.cache_data
def load_data(file_path):

    df = pd.read_csv(file_path)

    df.columns = df.columns.str.strip()

    df["Country"] = df["Country"].astype(str).str.strip()

    mbti_columns = [
        "ISTJ", "ISFJ", "INFJ", "INTJ",
        "ISTP", "ISFP", "INFP", "INTP",
        "ESTP", "ESFP", "ENFP", "ENTP",
        "ESTJ", "ESFJ", "ENFJ", "ENTJ"
    ]

    # MBTI 컬럼 확인
    missing_columns = [
        col for col in mbti_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"CSV 파일에 없는 MBTI 컬럼: {missing_columns}"
        )

    # 숫자로 변환
    for col in mbti_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df[mbti_columns] = df[mbti_columns].fillna(0)

    return df, mbti_columns


# 파일 존재 여부 확인
if not CSV_FILE.exists():

    st.error("CSV 파일을 찾을 수 없습니다.")

    st.write("현재 CSV 검색 경로:")
    st.code(str(CSV_FILE))

    st.stop()


try:
    df, mbti_columns = load_data(str(CSV_FILE))

except Exception as e:

    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")

    st.stop()


# ==========================================
# 4. 국가 선택
# ==========================================
countries = sorted(
    df["Country"].dropna().unique().tolist()
)

if not countries:
    st.error("CSV 파일에 국가 데이터가 없습니다.")
    st.stop()

default_index = (
    countries.index("South Korea")
    if "South Korea" in countries
    else 0
)

selected_country = st.selectbox(
    "🗺️ 분석할 국가를 선택하세요",
    countries,
    index=default_index
)


# ==========================================
# 5. 선택 국가의 MBTI 데이터
# ==========================================
country_data = df.loc[
    df["Country"] == selected_country,
    mbti_columns
].iloc[0]

# 원본 데이터가 소수 형태인지 확인
if country_data.max() <= 1:

    percentages = country_data * 100

else:

    percentages = country_data.copy()


# ==========================================
# 6. MBTI 순위 정렬
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
# 7. 상단 통계 표시
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
# 8. 그라데이션 색상 함수
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


# 1위: 쨍한 연두색
# 16위: 아주 연한 연두색
colors = [

    interpolate_color(
        "#7CFC00",
        "#EFF9D8",
        i / max(len(chart_data) - 1, 1)
    )

    for i in range(len(chart_data))

]


# ==========================================
# 9. 막대그래프 생성
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

        cliponaxis=False,

        hovertemplate=
        "<b>%{y}</b><br>" +
        "비율: %{x:.2f}%" +
        "<extra></extra>"

    )

)


# ==========================================
# 10. 그래프 디자인
# ==========================================
fig.update_layout(

    title=dict(

        text=f"📊 {selected_country}의 MBTI 유형별 비율",

        x=0.02,

        xanchor="left"

    ),

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
# 11. Streamlit 그래프 출력
# ==========================================
st.plotly_chart(

    fig,

    use_container_width=True

)


# ==========================================
# 12. MBTI 순위표
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
# 13. 데이터 안내
# ==========================================
st.info(
    "참고: 이 앱은 제공된 CSV 파일의 값을 시각화합니다. "
    "국가별 조사 표본과 데이터 출처에 따라 실제 인구의 "
    "MBTI 분포와 차이가 있을 수 있습니다."
)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="세계 MBTI 국가별 순위",
    page_icon="🌏",
    layout="wide"
)

st.title("🌏 세계 MBTI 국가별 순위")
st.markdown(
    "MBTI 유형을 선택하면 해당 유형의 비율이 높은 국가부터 순위를 보여줍니다."
)

# ==========================================
# 2. CSV 파일 경로
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent

CSV_FILE = BASE_DIR / "countriesMBTI_16types (1).csv"


# ==========================================
# 3. 데이터 불러오기
# ==========================================
@st.cache_data
def load_data(file_path):

    df = pd.read_csv(file_path)

    df.columns = df.columns.str.strip()

    df["Country"] = df["Country"].astype(str).str.strip()

    mbti_columns = [
        "ISTJ", "ISFJ", "INFJ", "INTJ",
        "ISTP", "ISFP", "INFP", "INTP",
        "ESTP", "ESFP", "ENFP", "ENTP",
        "ESTJ", "ESFJ", "ENFJ", "ENTJ"
    ]

    for col in mbti_columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df[mbti_columns] = df[mbti_columns].fillna(0)

    return df, mbti_columns


if not CSV_FILE.exists():

    st.error("CSV 파일을 찾을 수 없습니다.")

    st.code(str(CSV_FILE))

    st.stop()


try:

    df, mbti_columns = load_data(str(CSV_FILE))

except Exception as e:

    st.error(f"데이터 오류: {e}")

    st.stop()


# ==========================================
# 4. MBTI 선택
# ==========================================
st.subheader("🧠 MBTI 유형 선택")

selected_mbti = st.selectbox(
    "분석하고 싶은 MBTI를 선택하세요.",
    mbti_columns,
    index=mbti_columns.index("INFP")
)


# ==========================================
# 5. 선택한 MBTI의 국가별 비율
# ==========================================
country_data = df[
    ["Country", selected_mbti]
].copy()

country_data = country_data.rename(
    columns={
        selected_mbti: "비율"
    }
)

# 0~1 사이의 값이면 백분율로 변환
if country_data["비율"].max() <= 1:

    country_data["비율"] = (
        country_data["비율"] * 100
    )


# ==========================================
# 6. 높은 순서대로 국가 정렬
# ==========================================
country_data = country_data.sort_values(
    by="비율",
    ascending=False
).reset_index(drop=True)

# 순위 추가
country_data.insert(
    0,
    "순위",
    range(1, len(country_data) + 1)
)


# ==========================================
# 7. 상단 주요 통계
# ==========================================
top_country = country_data.iloc[0]["Country"]

top_value = country_data.iloc[0]["비율"]

second_country = country_data.iloc[1]["Country"]

second_value = country_data.iloc[1]["비율"]

average_value = country_data["비율"].mean()

col1, col2, col3 = st.columns(3)

col1.metric(
    "🥇 1위 국가",
    top_country,
    f"{top_value:.2f}%"
)

col2.metric(
    "🥈 2위 국가",
    second_country,
    f"{second_value:.2f}%"
)

col3.metric(
    "🌍 158개국 평균",
    f"{average_value:.2f}%"
)

st.divider()


# ==========================================
# 8. 그라데이션 색상 함수
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


# 1위: 쨍한 연두색
# 꼴찌: 아주 연한 연두색
colors = [

    interpolate_color(
        "#7CFC00",
        "#EFF9D8",
        i / max(len(country_data) - 1, 1)
    )

    for i in range(len(country_data))

]


# ==========================================
# 9. 그래프 데이터
# ==========================================
fig = go.Figure()

fig.add_trace(

    go.Bar(

        x=country_data["비율"],

        y=country_data["Country"],

        orientation="h",

        marker=dict(

            color=colors,

            line=dict(
                color="white",
                width=0.5
            )

        ),

        text=[
            f"{v:.2f}%"
            for v in country_data["비율"]
        ],

        textposition="outside",

        cliponaxis=False,

        hovertemplate=
        "<b>%{y}</b><br>" +
        "비율: %{x:.2f}%" +
        "<extra></extra>"

    )

)


# ==========================================
# 10. 그래프 디자인
# ==========================================
fig.update_layout(

    title=dict(

        text=f"📊 {selected_mbti} 비율이 높은 국가 순위",

        x=0.02

    ),

    xaxis=dict(

        title="국가별 MBTI 비율 (%)",

        rangemode="tozero",

        showgrid=True,

        gridcolor="rgba(120,120,120,0.15)",

        ticksuffix="%"

    ),

    yaxis=dict(

        title="국가",

        autorange="reversed"

    ),

    height=1000,

    margin=dict(

        l=30,

        r=80,

        t=80,

        b=50

    ),

    plot_bgcolor="rgba(0,0,0,0)",

    paper_bgcolor="rgba(0,0,0,0)",

    font=dict(size=12),

    showlegend=False

)


# ==========================================
# 11. 그래프 출력
# ==========================================
st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 12. 국가별 순위표
# ==========================================
st.subheader(f"🏆 {selected_mbti} 국가별 순위표")

with st.expander("전체 국가 순위표 보기", expanded=True):

    display_data = country_data.copy()

    display_data["비율"] = display_data["비율"].apply(
        lambda x: f"{x:.2f}%"
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 13. 데이터 안내
# ==========================================
st.info(
    "이 순위는 제공된 CSV 데이터에 기록된 국가별 MBTI 비율을 "
    "기준으로 계산한 결과입니다. 실제 국가 인구 전체의 "
    "MBTI 분포를 의미하지는 않습니다."
)

st.caption(
    "🌱 World MBTI Explorer | Made with Streamlit"
)


st.caption(
    "🌱 World MBTI Explorer | Made with Streamlit"
)
