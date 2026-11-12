
# ==================================================
# 1. 라이브러리 불러오기
# ==================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.ensemble import RandomForestRegressor


# ==================================================
# 2. 페이지 설정
# ==================================================
st.set_page_config(
    page_title="월별 기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온 예측")
st.write("과거 기온 데이터를 분석하여 미래 기온을 예측해 봅시다!")


# ==================================================
# 3. CSV 파일 경로 설정
# ==================================================
# 현재 파일은 pages 폴더 안에 있고
# CSV 파일은 상위 폴더에 있음

BASE_DIR = Path(__file__).resolve().parent.parent
FILE_PATH = BASE_DIR / "temperature.csv"


# ==================================================
# 4. CSV 데이터 불러오기
# ==================================================
@st.cache_data
def load_data():

    if not FILE_PATH.exists():
        raise FileNotFoundError(
            f"CSV 파일을 찾을 수 없습니다.\n{FILE_PATH}"
        )

    # 다양한 한글 인코딩 확인
    encodings = [
        "utf-8-sig",
        "cp949",
        "euc-kr"
    ]

    df = None
    used_encoding = None

    for encoding in encodings:
        try:
            df = pd.read_csv(
                FILE_PATH,
                encoding=encoding
            )
            used_encoding = encoding
            break

        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError(
            "CSV 파일의 인코딩을 읽을 수 없습니다."
        )

    # 열 이름 앞뒤 공백 제거
    df.columns = df.columns.astype(str).str.strip()

    # 필요한 열 확인
    required_columns = [
        "일시",
        "평균기온(℃)",
        "평균최고기온(℃)",
        "최고기온(℃)",
        "평균최저기온(℃)"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"CSV 파일에 다음 열이 없습니다: {missing_columns}\n"
            f"현재 열 이름: {list(df.columns)}"
        )

    # 날짜 변환
    df["날짜"] = pd.to_datetime(
        df["일시"].astype(str).str.strip(),
        format="%b-%y",
        errors="coerce"
    )

    # 기온을 숫자로 변환
    temperature_columns = [
        "평균기온(℃)",
        "평균최고기온(℃)",
        "최고기온(℃)",
        "평균최저기온(℃)"
    ]

    for col in temperature_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # 날짜가 없는 행 제거
    df = df.dropna(subset=["날짜"])

    # 연도와 월 추출
    df["연도"] = df["날짜"].dt.year
    df["월"] = df["날짜"].dt.month

    # 정렬
    df = df.sort_values("날짜")

    return df, used_encoding


# 데이터 불러오기
try:
    df, used_encoding = load_data()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


if df.empty:
    st.error("분석할 데이터가 없습니다.")
    st.stop()


# ==================================================
# 5. 데이터 정보 표시
# ==================================================
st.success(
    f"데이터 불러오기 성공! (인코딩: {used_encoding})"
)

st.caption(
    f"분석 데이터 기간: {df['연도'].min()}년 ~ {df['연도'].max()}년"
)


# ==================================================
# 6. 분석 조건 선택
# ==================================================
st.divider()
st.subheader("🔎 분석 조건 선택")

month_names = {
    1: "1월",
    2: "2월",
    3: "3월",
    4: "4월",
    5: "5월",
    6: "6월",
    7: "7월",
    8: "8월",
    9: "9월",
    10: "10월",
    11: "11월",
    12: "12월"
}

target_options = {
    "평균기온": "평균기온(℃)",
    "평균최고기온": "평균최고기온(℃)",
    "최고기온": "최고기온(℃)",
    "평균최저기온": "평균최저기온(℃)"
}

col1, col2, col3 = st.columns(3)

with col1:
    selected_month = st.selectbox(
        "분석할 월 선택",
        options=list(month_names.keys()),
        format_func=lambda x: month_names[x]
    )

with col2:
    selected_target = st.selectbox(
        "분석할 기온 선택",
        options=list(target_options.keys())
    )

with col3:
    selected_model = st.selectbox(
        "예측 알고리즘 선택",
        options=[
            "선형회귀",
            "다항회귀",
            "랜덤포레스트"
        ]
    )


# ==================================================
# 7. 예측할 연도 선택
# ==================================================
last_year = int(df["연도"].max())

selected_year = st.number_input(
    "🔮 예측할 연도",
    min_value=last_year,
    max_value=last_year + 30,
    value=last_year + 1,
    step=1
)

selected_year = int(selected_year)

target_column = target_options[selected_target]


# ==================================================
# 8. 선택한 월의 데이터 추출
# ==================================================
monthly_df = df[
    df["월"] == selected_month
][["연도", target_column]].copy()

monthly_df = monthly_df.dropna()
monthly_df = monthly_df.sort_values("연도")

# 같은 연도에 데이터가 여러 개 있으면 평균 계산
monthly_df = (
    monthly_df
    .groupby("연도", as_index=False)[target_column]
    .mean()
)

if len(monthly_df) < 3:
    st.warning(
        "예측하려면 선택한 월에 최소 3개 연도의 데이터가 필요합니다."
    )
    st.stop()

X = monthly_df["연도"].values.astype(float)
y = monthly_df[target_column].values.astype(float)

future_X = np.array([float(selected_year)])


# ==================================================
# 9. 회귀 알고리즘 함수
# ==================================================

# ① 선형회귀
def linear_prediction(X, y, predict_year):

    coefficients = np.polyfit(X, y, 1)

    model = np.poly1d(coefficients)

    return model(predict_year)


# ② 다항회귀
def polynomial_prediction(X, y, predict_year):

    coefficients = np.polyfit(X, y, 2)

    model = np.poly1d(coefficients)

    return model(predict_year)


# ③ 랜덤포레스트
def random_forest_prediction(X, y, predict_year):

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=4,
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X.reshape(-1, 1),
        y
    )

    return model.predict(
        predict_year.reshape(-1, 1)
    )


# ==================================================
# 10. 세 가지 알고리즘 예측 계산
# ==================================================
try:

    linear_result = linear_prediction(
        X, y, future_X
    )

    polynomial_result = polynomial_prediction(
        X, y, future_X
    )

    forest_result = random_forest_prediction(
        X, y, future_X
    )

    predictions = {
        "선형회귀": float(linear_result[0]),
        "다항회귀": float(polynomial_result[0]),
        "랜덤포레스트": float(forest_result[0])
    }

except Exception as e:

    st.error(f"예측 계산 중 오류가 발생했습니다: {e}")
    st.stop()


# 선택한 알고리즘의 예측값
selected_prediction = predictions[selected_model]


# ==================================================
# 11. 예측 결과 표시
# ==================================================
st.divider()
st.subheader("🔮 기온 예측 결과")

result_col1, result_col2 = st.columns(2)

with result_col1:

    st.metric(
        label=f"{selected_year}년 {month_names[selected_month]} 예측 기온",
        value=f"{selected_prediction:.1f}℃"
    )

with result_col2:

    st.metric(
        label="선택한 알고리즘",
        value=selected_model
    )


# ==================================================
# 12. 실제 기온과 예측 추세선 계산
# ==================================================
graph_years = np.arange(
    int(X.min()),
    selected_year + 1
)

graph_years_float = graph_years.astype(float)

if selected_model == "선형회귀":

    graph_values = linear_prediction(
        X,
        y,
        graph_years_float
    )

elif selected_model == "다항회귀":

    graph_values = polynomial_prediction(
        X,
        y,
        graph_years_float
    )

else:

    graph_model = RandomForestRegressor(
        n_estimators=300,
        max_depth=4,
        random_state=42,
        n_jobs=-1
    )

    graph_model.fit(
        X.reshape(-1, 1),
        y
    )

    graph_values = graph_model.predict(
        graph_years_float.reshape(-1, 1)
    )


# ==================================================
# 13. 실제 기온과 예측 그래프
# ==================================================
st.divider()

st.subheader(
    f"📈 {month_names[selected_month]} 월별 기온 분석"
)

fig = go.Figure()

# 실제 기온
fig.add_trace(
    go.Scatter(
        x=X,
        y=y,
        mode="lines+markers",
        name="실제 기온",
        line=dict(
            color="#2196F3",
            width=3
        ),
        marker=dict(size=7)
    )
)

# 예측 추세선
fig.add_trace(
    go.Scatter(
        x=graph_years,
        y=graph_values,
        mode="lines",
        name=f"{selected_model} 예측선",
        line=dict(
            color="#32CD32",
            width=3,
            dash="dash"
        )
    )
)

# 미래 예측값
fig.add_trace(
    go.Scatter(
        x=[selected_year],
        y=[selected_prediction],
        mode="markers+text",
        name="미래 예측값",
        text=[f"{selected_prediction:.1f}℃"],
        textposition="top center",
        marker=dict(
            color="#FF5722",
            size=13
        )
    )
)

fig.update_layout(
    title=f"{month_names[selected_month]} 월별 기온 분석",
    xaxis_title="연도",
    yaxis_title="기온 (℃)",
    hovermode="x unified",
    template="plotly_white",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==================================================
# 14. 세 가지 알고리즘 결과 비교
# ==================================================
st.divider()

st.subheader("📊 알고리즘별 예측 결과 비교")

comparison_df = pd.DataFrame({
    "알고리즘": list(predictions.keys()),
    "예측 기온(℃)": [
        round(value, 2)
        for value in predictions.values()
    ]
})

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)


# 비교 막대그래프
comparison_fig = go.Figure()

comparison_fig.add_trace(
    go.Bar(
        x=comparison_df["알고리즘"],
        y=comparison_df["예측 기온(℃)"],
        marker_color=[
            "#32CD32",
            "#90EE90",
            "#B8E6A3"
        ],
        text=[
            f"{value:.1f}℃"
            for value in comparison_df["예측 기온(℃)"]
        ],
        textposition="outside"
    )
)

comparison_fig.update_layout(
    title=f"{selected_year}년 {month_names[selected_month]} 알고리즘별 예측",
    xaxis_title="예측 알고리즘",
    yaxis_title="예측 기온 (℃)",
    template="plotly_white"
)

st.plotly_chart(
    comparison_fig,
    use_container_width=True
)


# ==================================================
# 15. 알고리즘 설명
# ==================================================
st.divider()

st.subheader("💡 회귀 알고리즘 알아보기")

with st.expander("① 선형회귀란?"):

    st.write("""
    선형회귀는 과거 데이터의 전체적인 직선 추세를 분석하는 방법입니다.

    - 데이터가 일정하게 증가하거나 감소하는 경향을 분석합니다.
    - 계산이 간단하고 결과를 이해하기 쉽습니다.
    - 직선 형태로 미래 기온을 예측합니다.
    """)


with st.expander("② 다항회귀란?"):

    st.write("""
    다항회귀는 직선이 아닌 곡선 형태의 추세를 분석하는 방법입니다.

    - 기온의 증가와 감소가 일정하지 않을 때 활용할 수 있습니다.
    - 데이터의 곡선 패턴을 학습합니다.
    - 먼 미래를 예측하면 실제와 차이가 커질 수 있습니다.
    """)


with st.expander("③ 랜덤포레스트란?"):

    st.write("""
    랜덤포레스트는 여러 개의 의사결정나무를 조합하는 알고리즘입니다.

    - 여러 나무의 예측 결과를 종합합니다.
    - 복잡한 데이터 패턴을 학습할 수 있습니다.
    - 학습한 연도 범위를 벗어난 미래 예측에는 한계가 있습니다.
    """)


# ==================================================
# 16. 데이터 안내
# ==================================================
st.divider()

st.info("""
📌 예측 결과는 과거 기온 데이터를 바탕으로 계산한 통계적 추정값입니다.

실제 미래 날씨를 보장하는 일기예보가 아니며,
특히 먼 미래의 예측은 실제 기온과 차이가 날 수 있습니다.
""")

st.caption("기온 데이터 분석 및 회귀 예측 프로그램")
