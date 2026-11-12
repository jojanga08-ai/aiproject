
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.ensemble import RandomForestRegressor

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="월별 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

# ==========================================
# 2. 화면 디자인
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
과거 기온 데이터를 활용하여 3가지 회귀 알고리즘으로
미래 평균기온을 예측하고 결과를 비교해 보세요!
""")

st.divider()

# ==========================================
# 4. CSV 파일 경로
# ==========================================
# 현재 PY 파일: aiproject/pages/06_기온예측.py
# CSV 파일: aiproject/temperature.csv

BASE_DIR = Path(__file__).resolve().parent.parent

file_path = BASE_DIR / "temperature.csv"

# temperature(1).csv 파일명도 지원
if not file_path.exists():
    file_path = BASE_DIR / "temperature(1).csv"

if not file_path.exists():
    st.error(f"CSV 파일을 찾을 수 없습니다: {file_path}")
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
    st.error(f"CSV 읽기 오류: {e}")
    st.stop()

# ==========================================
# 6. 필요한 데이터 확인
# ==========================================
required_columns = [
    "일시",
    "평균기온(℃)"
]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름을 확인해주세요.")
    st.write(df.columns.tolist())
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

def parse_date(date_text):

    try:
        month_text, year_text = str(date_text).strip().split("-")

        month = month_map[month_text.title()]
        year_number = int(year_text)

        if year_number < 100:
            if year_number <= 49:
                year = 2000 + year_number
            else:
                year = 1900 + year_number
        else:
            year = year_number

        return pd.Series([year, month])

    except (ValueError, KeyError):
        return pd.Series([np.nan, np.nan])


df[["연도", "월"]] = df["일시"].apply(parse_date)

df = df.dropna(subset=["연도", "월"])

df["연도"] = df["연도"].astype(int)
df["월"] = df["월"].astype(int)

df = df.sort_values(["연도", "월"])

# ==========================================
# 8. 월 선택 및 예측 연도 입력
# ==========================================
st.subheader("🔍 분석 조건 선택")

col1, col2 = st.columns(2)

with col1:

    selected_month = st.selectbox(
        "분석할 월 선택",
        range(1, 13),
        format_func=lambda x: f"{x}월"
    )

month_df = df[df["월"] == selected_month].copy()

if month_df.empty:
    st.error("선택한 월의 데이터가 없습니다.")
    st.stop()

with col2:

    latest_year = int(month_df["연도"].max())

    forecast_year = st.number_input(
        "예측할 연도 입력",
        min_value=latest_year + 1,
        max_value=2200,
        value=latest_year + 1,
        step=1
    )

# ==========================================
# 9. 알고리즘 선택
# ==========================================
st.subheader("🤖 회귀 알고리즘 선택")

algorithm_options = [
    "선형회귀 (Linear Regression)",
    "다항회귀 (Polynomial Regression)",
    "랜덤 포레스트 (Random Forest)"
]

selected_algorithm = st.selectbox(
    "사용할 알고리즘을 선택하세요",
    algorithm_options
)

# ==========================================
# 10. 분석 데이터 준비
# ==========================================
month_df = (
    month_df.groupby("연도", as_index=False)
    ["평균기온(℃)"]
    .mean()
)

month_df = month_df.sort_values("연도")

if len(month_df) < 3:
    st.error("분석을 위해 최소 3개 이상의 연도 데이터가 필요합니다.")
    st.stop()

x = month_df["연도"].to_numpy(dtype=float)
y = month_df["평균기온(℃)"].to_numpy(dtype=float)

# ==========================================
# 11. 회귀 알고리즘 계산
# ==========================================

# 연도 중심화
base_year = x.mean()
x_centered = x - base_year

# 추세선을 그리기 위한 연도
trend_years = np.linspace(
    x.min(),
    float(forecast_year),
    300
)

trend_centered = trend_years - base_year

predictions = {}
trend_results = {}

# ------------------------------------------
# ① 선형회귀
# ------------------------------------------
linear_coef = np.polyfit(
    x_centered,
    y,
    1
)

linear_prediction = np.polyval(
    linear_coef,
    float(forecast_year) - base_year
)

linear_trend = np.polyval(
    linear_coef,
    trend_centered
)

predictions[algorithm_options[0]] = linear_prediction
trend_results[algorithm_options[0]] = linear_trend

# ------------------------------------------
# ② 다항회귀 (2차)
# ------------------------------------------
poly_coef = np.polyfit(
    x_centered,
    y,
    2
)

poly_prediction = np.polyval(
    poly_coef,
    float(forecast_year) - base_year
)

poly_trend = np.polyval(
    poly_coef,
    trend_centered
)

predictions[algorithm_options[1]] = poly_prediction
trend_results[algorithm_options[1]] = poly_trend

# ------------------------------------------
# ③ 랜덤 포레스트 회귀
# ------------------------------------------
rf_model = RandomForestRegressor(
    n_estimators=300,
    max_depth=4,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(
    x.reshape(-1, 1),
    y
)

rf_prediction = rf_model.predict(
    np.array([[float(forecast_year)]])
)[0]

rf_trend = rf_model.predict(
    trend_years.reshape(-1, 1)
)

predictions[algorithm_options[2]] = rf_prediction
trend_results[algorithm_options[2]] = rf_trend

# ==========================================
# 12. 선택한 알고리즘 결과
# ==========================================
selected_prediction = predictions[selected_algorithm]

st.divider()

st.subheader(
    f"📊 {selected_month}월 평균기온 예측 결과"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "분석 데이터",
        f"{len(month_df)}개"
    )

with col2:
    st.metric(
        "최근 관측 평균기온",
        f"{y[-1]:.1f} ℃"
    )

with col3:
    st.metric(
        f"{int(forecast_year)}년 예측기온",
        f"{selected_prediction:.2f} ℃"
    )

st.info(f"선택한 알고리즘: {selected_algorithm}")

# ==========================================
# 13. 그래프 생성
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
            color="white",
            size=8
        )
    )
)

# 알고리즘별 색상
algorithm_colors = {
    algorithm_options[0]: "#39FF14",
    algorithm_options[1]: "#00BFFF",
    algorithm_options[2]: "#FF4DCE"
}

# 세 알고리즘 추세선
for name in algorithm_options:

    is_selected = name == selected_algorithm

    fig.add_trace(
        go.Scatter(
            x=trend_years,
            y=trend_results[name],
            mode="lines",
            name=name,
            line=dict(
                color=algorithm_colors[name],
                width=4 if is_selected else 2
            ),
            opacity=1.0 if is_selected else 0.55
        )
    )

# 선택한 알고리즘의 예측값
fig.add_trace(
    go.Scatter(
        x=[forecast_year],
        y=[selected_prediction],
        mode="markers+text",
        name="선택한 알고리즘 예측값",
        marker=dict(
            color="white",
            size=15,
            symbol="star",
            line=dict(
                color=algorithm_colors[selected_algorithm],
                width=3
            )
        ),
        text=[f"{selected_prediction:.2f}℃"],
        textposition="top center",
        textfont=dict(
            color="white",
            size=14
        )
    )
)

fig.update_layout(
    title=dict(
        text=f"{selected_month}월 평균기온 - 알고리즘 비교",
        font=dict(size=22, color="white")
    ),
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    template="plotly_dark",
    paper_bgcolor="#111111",
    plot_bgcolor="#111111",
    font=dict(color="white"),
    height=650,
    hovermode="x unified",
    legend=dict(
        bgcolor="#222222",
        font=dict(color="white")
    ),
    xaxis=dict(
        gridcolor="#555555",
        dtick=2
    ),
    yaxis=dict(
        gridcolor="#555555"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================
# 14. 예측 결과 비교
# ==========================================
st.divider()

st.subheader("🏆 세 가지 알고리즘 예측값 비교")

comparison_df = pd.DataFrame({
    "알고리즘": list(predictions.keys()),
    "예측 평균기온(℃)": [
        round(value, 2)
        for value in predictions.values()
    ]
})

comparison_df["선택 여부"] = [
    "⭐ 선택됨" if name == selected_algorithm else ""
    for name in comparison_df["알고리즘"]
]

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)

difference = (
    max(predictions.values())
    - min(predictions.values())
)

st.metric(
    "알고리즘별 예측값 최대 차이",
    f"{difference:.2f} ℃"
)

# ==========================================
# 15. 알고리즘 작동 원리 설명
# ==========================================
st.divider()

st.subheader("📚 회귀 알고리즘 작동 원리")

if selected_algorithm == algorithm_options[0]:

    st.markdown("""
    ### ① 선형회귀 (Linear Regression)

    데이터를 가장 잘 설명하는 직선을 찾는 알고리즘입니다.

    **작동 과정**

    1. 과거 평균기온을 점으로 표시합니다.
    2. 점들과 가장 잘 맞는 직선을 계산합니다.
    3. 오차 제곱 합이 최소가 되도록 직선을 조정합니다.
    4. 직선을 미래까지 연장하여 기온을 예측합니다.
    """)

    st.latex(r"\hat{y}=ax+b")

    st.markdown("""
    **특징:** 전체적인 상승 및 하락 추세를 파악하기 좋습니다.
    """)

elif selected_algorithm == algorithm_options[1]:

    st.markdown("""
    ### ② 다항회귀 (Polynomial Regression)

    데이터를 직선이 아닌 곡선으로 표현하는 알고리즘입니다.

    이번 프로그램에서는 2차 다항회귀를 사용합니다.

    **작동 과정**

    1. 과거 기온 데이터의 곡선 형태를 분석합니다.
    2. 데이터에 잘 맞는 2차 곡선을 계산합니다.
    3. 곡선을 미래 연도까지 연장하여 예측합니다.
    """)

    st.latex(r"\hat{y}=ax^2+bx+c")

    st.markdown("""
    **특징:** 직선으로 표현하기 어려운 변화 패턴을 분석할 수 있습니다.

    **주의:** 먼 미래에는 곡선이 급격하게 변할 수 있습니다.
    """)

else:

    st.markdown("""
    ### ③ 랜덤 포레스트 회귀 (Random Forest Regression)

    여러 개의 의사결정나무를 결합하여 예측하는 알고리즘입니다.

    **작동 과정**

    1. 과거 데이터에서 여러 학습용 표본을 만듭니다.
    2. 각 표본을 이용하여 의사결정나무를 학습합니다.
    3. 여러 나무가 각각 기온을 예측합니다.
    4. 예측 결과의 평균을 계산합니다.

    **특징**

    - 복잡한 비선형 패턴을 학습할 수 있습니다.
    - 여러 의사결정나무를 결합합니다.
    - 데이터의 복잡한 관계를 분석하는 데 유용합니다.

    **주의:** 과거 데이터 범위를 벗어난 미래 예측에는 한계가 있습니다.
    예측값이 과거 관측 기온 범위에 가까워질 수 있습니다.
    """)

# ==========================================
# 16. 알고리즘 비교표
# ==========================================
st.divider()

st.subheader("📖 알고리즘 특징 비교")

feature_df = pd.DataFrame({
    "알고리즘": [
        "선형회귀",
        "다항회귀",
        "랜덤 포레스트"
    ],
    "그래프 형태": [
        "직선",
        "곡선",
        "계단형 변화 가능"
    ],
    "학습 방식": [
        "최적 직선 계산",
        "최적 다항식 계산",
        "여러 의사결정나무 결합"
    ],
    "장점": [
        "쉽고 빠름",
        "곡선 패턴 분석",
        "복잡한 패턴 학습"
    ],
    "한계": [
        "곡선 반영 어려움",
        "미래 외삽 주의",
        "미래 외삽에 약함"
    ]
})

st.dataframe(
    feature_df,
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 17. 실제 데이터 확인
# ==========================================
with st.expander("📋 분석에 사용된 실제 기온 데이터"):

    st.dataframe(
        month_df,
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# 18. 하단 안내
# ==========================================
st.caption(
    "데이터 출처: temperature.csv"
)

st.caption(
    "알고리즘: Linear Regression / "
    "Polynomial Regression / Random Forest Regression"
)

st.caption(
    "※ 예측 결과는 과거 데이터에 기반한 통계적 추정치이며 "
    "실제 미래 기온과 다를 수 있습니다."
)
