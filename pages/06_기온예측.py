
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
과거 기온 데이터를 활용하여 3가지 회귀 알고리즘으로
미래의 평균기온을 예측하고 결과를 비교해 보세요!
""")

st.divider()

# ==========================================
# 4. CSV 파일 불러오기
# ==========================================
# py 파일: aiproject/pages/
# csv 파일: aiproject/

BASE_DIR = Path(__file__).resolve().parent.parent

file_path = BASE_DIR / "temperature.csv"

# 원래 업로드 파일명도 지원
if not file_path.exists():
    file_path = BASE_DIR / "temperature(1).csv"

if not file_path.exists():
    st.error(
        f"CSV 파일을 찾을 수 없습니다.\n\n"
        f"확인한 경로: {file_path}"
    )
    st.stop()

try:
    try:
        df = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8-sig")

except Exception as e:
    st.error(f"CSV 파일 읽기 오류: {e}")
    st.stop()

# ==========================================
# 5. 데이터 확인 및 정리
# ==========================================
required_columns = ["일시", "평균기온(℃)"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일에 필요한 열이 없습니다.")
    st.write("현재 열 이름:", df.columns.tolist())
    st.stop()

df = df[required_columns].copy()

df["평균기온(℃)"] = pd.to_numeric(
    df["평균기온(℃)"],
    errors="coerce"
)

df = df.dropna()

# ==========================================
# 6. 날짜에서 연도와 월 추출
# ==========================================
month_map = {
    "Jan": 1, "Feb": 2, "Mar": 3,
    "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9,
    "Oct": 10, "Nov": 11, "Dec": 12
}

def parse_date(date_text):

    try:
        month_text, year_text = str(date_text).strip().split("-")

        month = month_map[month_text.title()]
        year_number = int(year_text)

        if year_number < 100:
            # 00~49는 2000년대
            # 50~99는 1900년대
            year = (
                2000 + year_number
                if year_number < 50
                else 1900 + year_number
            )
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
# 7. 사용자 입력
# ==========================================
st.subheader("🔍 분석 조건 선택")

col1, col2 = st.columns(2)

with col1:

    selected_month = st.selectbox(
        "분석할 월을 선택하세요",
        range(1, 13),
        format_func=lambda x: f"{x}월"
    )

with col2:

    available_data = df[df["월"] == selected_month]

    if available_data.empty:
        st.error("선택한 월의 데이터가 없습니다.")
        st.stop()

    latest_year = int(available_data["연도"].max())

    forecast_year = st.number_input(
        "예측할 연도를 입력하세요",
        min_value=latest_year + 1,
        max_value=2200,
        value=latest_year + 1,
        step=1
    )

# ==========================================
# 8. 알고리즘 선택
# ==========================================
st.subheader("🤖 회귀 알고리즘 선택")

algorithm_options = [
    "선형회귀 (Linear Regression)",
    "다항회귀 (Polynomial Regression)",
    "랜덤 포레스트 회귀 (Random Forest)"
]

selected_algorithm = st.selectbox(
    "사용할 예측 알고리즘을 선택하세요",
    algorithm_options
)

# ==========================================
# 9. 선택한 월의 데이터 추출
# ==========================================
month_df = df[df["월"] == selected_month].copy()

month_df = (
    month_df.groupby("연도", as_index=False)
    ["평균기온(℃)"].mean()
)

month_df = month_df.sort_values("연도")

if len(month_df) < 3:
    st.error("회귀 분석을 위해 최소 3개 연도의 데이터가 필요합니다.")
    st.stop()

x = month_df["연도"].to_numpy(dtype=float)
y = month_df["평균기온(℃)"].to_numpy(dtype=float)

# ==========================================
# 10. 회귀 알고리즘 3개 만들기
# ==========================================

# 연도 중심화: 다항회귀 계산의 수치 안정성 향상
base_year = x.mean()
x_centered = x - base_year

# 그래프에 표시할 연도
trend_years = np.linspace(
    x.min(),
    float(forecast_year),
    300
)

trend_centered = trend_years - base_year

# 미래 예측값 저장
predictions = {}

# 추세선 저장
trend_results = {}

# ------------------------------------------
# ① 선형회귀
# ------------------------------------------
linear_coef = np.polyfit(x_centered, y, 1)

linear_prediction = np.polyval(
    linear_coef,
    float(forecast_year) - base_year
)

linear_trend = np.polyval(
    linear_coef,
    trend_centered
)

predictions["선형회귀 (Linear Regression)"] = linear_prediction

trend_results["선형회귀 (Linear Regression)"] = linear_trend

# ------------------------------------------
# ② 다항회귀
# ------------------------------------------
# 2차 다항회귀
# 곡선 형태로 기온 변화 추세 학습

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

predictions["다항회귀 (Polynomial Regression)"] = poly_prediction

trend_results["다항회귀 (Polynomial Regression)"] = poly_trend

# ------------------------------------------
# ③ 랜덤 포레스트 회귀
# ------------------------------------------
rf_model = RandomForestRegressor(
    n_estimators=300,
    max_depth=4,
    random_state=42
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

predictions["랜덤 포레스트 회귀 (Random Forest)"] = rf_prediction

trend_results["랜덤 포레스트 회귀 (Random Forest)"] = rf_trend

# ==========================================
# 11. 선택한 알고리즘 결과
# ==========================================
selected_prediction = predictions[selected_algorithm]

st.divider()

st.subheader(
    f"📊 {selected_month}월 평균기온 예측 결과"
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
        f"{int(forecast_year)}년 예측기온",
        f"{selected_prediction:.2f} ℃"
    )

st.info(
    f"현재 선택한 알고리즘: {selected_algorithm}"
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
            color="white",
            size=8
        )
    )
)

# 알고리즘별 색상
algorithm_colors = {
    "선형회귀 (Linear Regression)": "#39FF14",
    "다항회귀 (Polynomial Regression)": "#00BFFF",
    "랜덤 포레스트 회귀 (Random Forest)": "#FF4DCE"
}

# 세 가지 알고리즘 추세선
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

# 선택한 알고리즘의 미래 예측값
fig.add_trace(
    go.Scatter(
        x=[forecast_year],
        y=[selected_prediction],
        mode="markers+text",
        name="선택한 알고리즘의 예측값",
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

# 그래프 디자인
fig.update_layout(
    title=dict(
        text=f"{selected_month}월 평균기온 - 회귀 알고리즘 비교",
        font=dict(
            size=22,
            color="white"
        )
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
# 13. 알고리즘별 예측값 비교
# ==========================================
st.divider()

st.subheader("🏆 3가지 알고리즘 예측 결과 비교")

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

# 예측값 차이
max_prediction = max(predictions.values())
min_prediction = min(predictions.values())

st.metric(
    "세 알고리즘의 예측값 차이",
    f"{max_prediction - min_prediction:.2f} ℃"
)

# ==========================================
# 14. 알고리즘별 작동 원리
# ==========================================
st.divider()

st.subheader("📚 회귀 알고리즘 작동 원리")

if selected_algorithm == algorithm_options[0]:

    st.markdown("""
    ### ① 선형회귀 (Linear Regression)

    선형회귀는 데이터의 전체적인 관계를 직선으로 나타냅니다.

    **작동 원리**

    1. 과거 연도별 평균기온을 점으로 표시합니다.
    2. 데이터와 가장 잘 맞는 직선을 찾습니다.
    3. 실제 기온과 직선의 오차 제곱 합을 최소화합니다.
    4. 계산된 직선을 미래까지 연장하여 기온을 예측합니다.

    **수학 공식**

    """)

    st.latex(r"\hat{y}=ax+b")

    st.markdown("""
    - a: 기울기
    - b: 절편
    - x: 연도
    - y: 예측 평균기온

    **특징:** 전체적인 상승 및 하락 추세를 파악하기 좋습니다.
    """)

elif selected_algorithm == algorithm_options[1]:

    st.markdown("""
    ### ② 다항회귀 (Polynomial Regression)

    다항회귀는 데이터를 곡선 형태로 분석하는 회귀 알고리즘입니다.

    이번 프로그램은 2차 다항회귀를 사용합니다.

    **작동 원리**

    1. 과거 기온 데이터의 곡선 형태를 분석합니다.
    2. 데이터에 잘 맞는 2차 곡선을 계산합니다.
    3. 곡선의 변화 추세를 바탕으로 미래 기온을 예측합니다.

    **수학 공식**
    """)

    st.latex(r"\hat{y}=ax^2+bx+c")

    st.markdown("""
    - a: 곡선의 굽어지는 정도
    - b: 기울기와 관련된 계수
    - c: 절편

    **특징:** 직선으로 표현하기 어려운 기온 변화 패턴을 표현할 수 있습니다.

    **주의:** 먼 미래로 갈수록 곡선이 급격히 변할 수 있습니다.
    """)

else:

    st.markdown("""
    ### ③ 랜덤 포레스트 회귀 (Random Forest Regression)

    랜덤 포레스트는 여러 개의 의사결정나무를 결합하는 알고리즘입니다.

    **작동 원리**

    1. 과거 데이터에서 여러 개의 학습용 표본을 구성합니다.
    2. 각 표본으로 의사결정나무를 학습합니다.
    3. 각각의 나무가 기온을 예측합니다.
    4. 여러 나무의 예측 결과를 평균하여 최종 기온을 계산합니다.

    **특징**

    - 복잡한 비선형 패턴을 학습할 수 있습니다.
    - 여러 의사결정나무를 사용합니다.
    - 직선이나 단순 곡선으로 표현하기 어려운 관계를 학습할 수 있습니다.

    **주의:** 과거 학습 범위 밖의 미래 연도에서는 새로운 기온 추세를 외삽하기 어렵습니다.
    예측값이 과거 데이터 범위의 값에 가까워질 수 있습니다.
    """)

# ==========================================
# 15. 세 알고리즘 한눈에 비교
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
        "단순하고 해석하기 쉬움",
        "곡선 패턴 분석",
        "복잡한 관계 학습"
    ],

    "한계": [
        "곡선 패턴 반영 어려움",
        "미래 외삽에 주의",
        "미래 외삽에 약함"
    ]
})

st.dataframe(
    feature_df,
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 16. 실제 데이터 확인
# ==========================================
with st.expander("📋 분석에 사용된 실제 기온 데이터"):

    st.dataframe(
        month_df,
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# 17. 안내
# ==========================================
st.caption(
    "데이터: temperature.csv | "
    "알고리즘: Linear Regression, "
    "Polynomial Regression, Random Forest Regression"
)

st.caption(
    "※ 예측값은 과거 데이터에 기반한 통계적 추정치이며 "
    "실제 미래 기온과 다를 수 있습니다."
)
