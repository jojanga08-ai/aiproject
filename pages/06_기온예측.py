
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="월별 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

# ==========================================
# 2. 디자인 설정
# ==========================================
st.markdown("""
<style>
.stApp {
    background-color: #111111;
    color: white;
}

h1, h2, h3, p, label {
    color: white !important;
}

div[data-testid="stMetric"] {
    background-color: #222222;
    padding: 18px;
    border-radius: 12px;
}

div[data-testid="stMetricValue"] {
    color: #39FF14 !important;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 제목
# ==========================================
st.title("🌡️ 월별 평균기온 예측 분석")

st.markdown("""
과거의 평균기온 데이터를 분석하고
선형회귀 알고리즘으로 미래 기온을 예측합니다.
""")

st.divider()

# ==========================================
# 4. CSV 파일 경로 설정
# ==========================================
# 현재 py 파일 위치: aiproject/pages/
# CSV 파일 위치: aiproject/
# parent.parent를 이용해 상위 폴더로 이동

BASE_DIR = Path(__file__).resolve().parent.parent

file_path = BASE_DIR / "temperature.csv"

# 파일 존재 여부 확인
if not file_path.exists():
    st.error(
        f"CSV 파일을 찾을 수 없습니다.\n\n"
        f"확인한 경로: {file_path}"
    )
    st.stop()

# ==========================================
# 5. CSV 파일 읽기
# ==========================================
try:
    try:
        df = pd.read_csv(
            file_path,
            encoding="cp949"
        )
    except UnicodeDecodeError:
        df = pd.read_csv(
            file_path,
            encoding="utf-8-sig"
        )

except Exception as e:
    st.error(f"CSV 파일 읽기 오류: {e}")
    st.stop()

# ==========================================
# 6. 데이터 확인
# ==========================================
required_columns = [
    "일시",
    "평균기온(℃)"
]

if not all(col in df.columns for col in required_columns):
    st.error(
        "CSV 파일에 '일시', '평균기온(℃)' 열이 있는지 확인해주세요."
    )
    st.write("현재 CSV 열:", df.columns.tolist())
    st.stop()

df = df[required_columns].copy()

df["평균기온(℃)"] = pd.to_numeric(
    df["평균기온(℃)"],
    errors="coerce"
)

df = df.dropna()

# ==========================================
# 7. 날짜에서 연도와 월 추출
# ==========================================
month_map = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}

years = []
months = []

century = 1900
previous_year = None

for date_text in df["일시"]:

    try:
        month_text, year_text = str(date_text).strip().split("-")

        month = month_map[month_text.title()]
        short_year = int(year_text)

        # 연도가 99에서 00으로 바뀌면 세기 변경
        if previous_year is not None:
            if short_year < previous_year:
                century += 100

        year = century + short_year

        years.append(year)
        months.append(month)

        previous_year = short_year

    except (ValueError, KeyError):
        years.append(None)
        months.append(None)

df["연도"] = years
df["월"] = months

df = df.dropna(
    subset=["연도", "월"]
)

df["연도"] = df["연도"].astype(int)
df["월"] = df["월"].astype(int)

df = df.sort_values(
    ["연도", "월"]
)

# ==========================================
# 8. 사용자 입력
# ==========================================
st.subheader("🔍 분석 조건 선택")

col1, col2 = st.columns(2)

with col1:

    selected_month = st.selectbox(
        "분석할 월을 선택하세요",
        list(range(1, 13)),
        format_func=lambda x: f"{x}월"
    )

with col2:

    available_month_data = df[
        df["월"] == selected_month
    ]

    if available_month_data.empty:
        st.error("선택한 월의 데이터가 없습니다.")
        st.stop()

    latest_year = int(
        available_month_data["연도"].max()
    )

    forecast_year = st.number_input(
        "예측할 연도를 입력하세요",
        min_value=latest_year + 1,
        max_value=2200,
        value=latest_year + 1,
        step=1
    )

# ==========================================
# 9. 선택한 월의 평균기온 데이터 추출
# ==========================================
month_df = df[
    df["월"] == selected_month
].copy()

# 같은 연도에 여러 데이터가 있으면 평균 계산
month_df = (
    month_df.groupby("연도", as_index=False)
    ["평균기온(℃)"]
    .mean()
)

month_df = month_df.sort_values("연도")

if len(month_df) < 2:
    st.error(
        "선형회귀 분석을 위해서는 "
        "최소 2개 이상의 연도 데이터가 필요합니다."
    )
    st.stop()

# ==========================================
# 10. 선형회귀 알고리즘
# ==========================================
x = month_df["연도"].to_numpy(dtype=float)

y = month_df["평균기온(℃)"].to_numpy(dtype=float)

# 직선의 기울기와 절편 계산
# y = ax + b

slope, intercept = np.polyfit(x, y, 1)

# 기존 데이터의 회귀값
fitted_y = slope * x + intercept

# 미래 기온 예측
predicted_temp = (
    slope * forecast_year + intercept
)

# 회귀 추세선
trend_years = np.linspace(
    x.min(),
    forecast_year,
    300
)

trend_temps = (
    slope * trend_years + intercept
)

# ==========================================
# 11. 예측 결과 출력
# ==========================================
st.divider()

st.subheader(
    f"📊 {selected_month}월 평균기온 분석 결과"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "분석 데이터 개수",
        f"{len(month_df)}개"
    )

with col2:
    st.metric(
        "최근 관측 평균기온",
        f"{y[-1]:.1f} ℃"
    )

with col3:
    st.metric(
        f"{int(forecast_year)}년 예측 평균기온",
        f"{predicted_temp:.1f} ℃"
    )

# ==========================================
# 12. 그래프 생성
# ==========================================
fig = go.Figure()

# 실제 관측 데이터
fig.add_trace(
    go.Scatter(
        x=x,
        y=y,
        mode="markers",
        name="실제 평균기온",
        marker=dict(
            color="#39FF14",
            size=8
        ),
        hovertemplate=
        "%{x}년<br>실제 기온: %{y:.1f}℃<extra></extra>"
    )
)

# 선형회귀 추세선
fig.add_trace(
    go.Scatter(
        x=trend_years,
        y=trend_temps,
        mode="lines",
        name="선형회귀 추세선",
        line=dict(
            color="#39FF14",
            width=3
        ),
        hovertemplate=
        "연도: %{x:.1f}<br>회귀값: %{y:.2f}℃<extra></extra>"
    )
)

# 미래 예측값
fig.add_trace(
    go.Scatter(
        x=[forecast_year],
        y=[predicted_temp],
        mode="markers+text",
        name="미래 예측기온",
        marker=dict(
            color="white",
            size=14,
            symbol="star",
            line=dict(
                color="#39FF14",
                width=3
            )
        ),
        text=[
            f"{predicted_temp:.1f}℃"
        ],
        textposition="top center",
        textfont=dict(
            color="#39FF14",
            size=15
        )
    )
)

# ==========================================
# 13. 그래프 디자인
# ==========================================
fig.update_layout(
    title=dict(
        text=f"{selected_month}월 평균기온 및 선형회귀 예측",
        font=dict(
            size=23,
            color="white"
        )
    ),

    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",

    template="plotly_dark",

    paper_bgcolor="#111111",
    plot_bgcolor="#111111",

    font=dict(
        color="white",
        size=13
    ),

    height=600,

    hovermode="x unified",

    legend=dict(
        font=dict(color="white"),
        bgcolor="#222222"
    ),

    xaxis=dict(
        gridcolor="#555555",
        dtick=10
    ),

    yaxis=dict(
        gridcolor="#555555",
        zerolinecolor="#777777"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================
# 14. 선형회귀 계산 과정
# ==========================================
st.divider()

st.subheader("🧮 선형회귀 계산 과정")

st.markdown("""
선형회귀 알고리즘은 과거 데이터에 가장 잘 맞는
직선을 찾아 미래의 기온을 예측합니다.
""")

st.latex(
    r"\hat{y} = ax+b"
)

st.write(
    f"**기울기(a):** {slope:.6f}"
)

st.write(
    f"**절편(b):** {intercept:.6f}"
)

st.write(
    f"**예측 연도:** {int(forecast_year)}년"
)

st.write(
    f"**예측 평균기온:** {predicted_temp:.2f} ℃"
)

# ==========================================
# 15. 선형회귀 알고리즘 설명
# ==========================================
st.divider()

st.subheader("📚 선형회귀 알고리즘이란?")

st.markdown("""
### ① 선형회귀란?

선형회귀(Linear Regression)는 과거 데이터를
이용하여 변수 사이의 관계를 직선으로 나타내고,
이를 바탕으로 새로운 값을 예측하는 알고리즘입니다.

### ② 이번 프로그램에서는?

- X축: 연도
- Y축: 선택한 월의 평균기온
- 입력 데이터: 과거의 월별 평균기온
- 출력 데이터: 미래 연도의 예상 평균기온

### ③ 어떻게 작동할까?

1. 과거 평균기온을 그래프의 점으로 표시합니다.
2. 각 점과 가장 잘 맞는 직선을 계산합니다.
3. 실제 데이터와 직선 사이의 오차 제곱 합이 최소가 되도록 기울기와 절편을 계산합니다.
4. 직선을 미래 연도까지 연장합니다.
5. 미래 연도의 위치에서 예상 기온을 계산합니다.

### ④ 장점

- 원리가 쉽고 이해하기 좋습니다.
- 계산 속도가 빠릅니다.
- 기온의 전반적인 상승 및 하락 추세를 확인할 수 있습니다.

### ⑤ 한계

- 기온은 다양한 기후 요인의 영향을 받습니다.
- 직선만으로 복잡한 기후 변화를 모두 설명할 수 없습니다.
- 실제 미래 기온과 예측값은 다를 수 있습니다.

따라서 이 프로그램의 예측 결과는
통계적인 추세를 이용한 참고용 값입니다.
""")

# ==========================================
# 16. 실제 데이터 확인
# ==========================================
with st.expander("📋 분석에 사용된 과거 데이터 확인"):

    st.dataframe(
        month_df,
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# 17. 하단 안내
# ==========================================
st.caption(
    "데이터 출처: temperature.csv | "
    "예측 알고리즘: 단순 선형회귀"
)
