
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.ensemble import RandomForestRegressor


# --------------------------------------------------
# 1. 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온 예측")
st.write("월과 예측 알고리즘을 선택하여 미래의 기온을 예측해 보세요!")


# --------------------------------------------------
# 2. CSV 파일 불러오기
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
FILE_PATH = BASE_DIR / "temperature.csv"


@st.cache_data
def load_data():
    if not FILE_PATH.exists():
        raise FileNotFoundError(
            f"CSV 파일을 찾을 수 없습니다: {FILE_PATH}"
        )

    df = pd.read_csv(FILE_PATH, encoding="utf-8-sig")

    required_columns = [
        "일시",
        "평균기온(℃)",
        "평균최고기온(℃)",
        "최고기온(℃)",
        "평균최저기온(℃)",
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"CSV 파일에 필요한 열이 없습니다: {missing}"
        )

    # 날짜 변환: Oct-07 형식 처리
    df["날짜"] = pd.to_datetime(
        df["일시"].astype(str).str.strip(),
        format="%b-%y",
        errors="coerce"
    )

    # 기온 데이터 숫자로 변환
    for col in required_columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["날짜"])

    df["연도"] = df["날짜"].dt.year
    df["월"] = df["날짜"].dt.month

    return df.sort_values("날짜")


try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


if df.empty:
    st.error("분석할 데이터가 없습니다.")
    st.stop()


# --------------------------------------------------
# 3. 사용자 선택
# --------------------------------------------------
st.subheader("🔎 분석 조건 선택")

month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

col1, col2, col3 = st.columns(3)

with col1:
    selected_month = st.selectbox(
        "분석할 월",
        options=list(month_names.keys()),
        format_func=lambda x: month_names[x]
    )

with col2:
    target_options = {
        "평균기온": "평균기온(℃)",
        "평균최고기온": "평균최고기온(℃)",
        "최고기온": "최고기온(℃)",
        "평균최저기온": "평균최저기온(℃)"
    }

    selected_target_name = st.selectbox(
        "예측할 기온",
        options=list(target_options.keys())
    )

with col3:
    selected_model = st.selectbox(
        "예측 알고리즘",
        [
            "선형회귀",
            "다항회귀",
            "랜덤포레스트"
        ]
    )


# 미래 예측 연도
last_year = int(df["연도"].max())

selected_year = st.number_input(
    "예측할 연도",
    min_value=last_year,
    max_value=last_year + 30,
    value=last_year + 1,
    step=1
)

target_column = target_options[selected_target_name]


# --------------------------------------------------
# 4. 선택한 월의 데이터 추출
# --------------------------------------------------
monthly_df = df[
    df["월"] == selected_month
][["연도", target_column]].copy()

monthly_df = monthly_df.dropna()
monthly_df = monthly_df.sort_values("연도")

if len(monthly_df) < 3:
    st.warning("선택한 월의 데이터가 3개 연도 이상 있어야 예측할 수 있습니다.")
    st.stop()


X = monthly_df["연도"].values.astype(float)
y = monthly_df[target_column].values.astype(float)

future_X = np.array([float(selected_year)])


# --------------------------------------------------
# 5. 세 가지 회귀 알고리즘
# --------------------------------------------------

def linear_prediction(X, y, predict_year):
    coefficients = np.polyfit(X, y, 1)
    model = np.poly1d(coefficients)

    return model(predict_year)


def polynomial_prediction(X, y, predict_year):
    coefficients = np.polyfit(X, y, 2)
    model = np.poly1d(coefficients)

    return model(predict_year)


def random_forest_prediction(X, y, predict_year):
    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=4,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X.reshape(-1, 1), y)

    return model.predict(
        predict_year.reshape(-1, 1)
    )


# --------------------------------------------------
# 6. 세 알고리즘의 예측 결과 계산
# --------------------------------------------------
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

except Exception as e:
    st.error(f"예측 계산 중 오류가 발생했습니다: {e}")
    st.stop()


predictions = {
    "선형회귀": float(linear_result[0]),
    "다항회귀": float(polynomial_result[0]),
    "랜덤포레스트": float(forest_result[0])
}

selected_prediction = predictions[selected_model]


# --------------------------------------------------
# 7. 그래프에 사용할 추세선 계산
# --------------------------------------------------
graph_years = np.arange(
    int(X.min()),
    int(selected_year) + 1
)

graph_years_float = graph_years.astype(float)

if selected_model == "선형회귀":
    graph_values = linear_prediction(
        X, y, graph_years_float
    )

elif selected_model == "다항회귀":
    graph_values = polynomial_prediction(
        X, y, graph_years_float
    )

else:
    graph_model = RandomForestRegressor(
        n_estimators=300,
        max_depth=4,
        random_state=42,
        n_jobs=-1
    )

    graph_model.fit(X.reshape(-1, 1), y)

    graph_values = graph_model.predict(
        graph_years_float.reshape(-1, 1)
    )


# --------------------------------------------------
# 8. 예측 결과 표시
# --------------------------------------------------
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
        label="선택한 예측 알고리즘",
        value=selected_model
    )


# --------------------------------------------------
# 9. 실제 기온과 예측 추세선 그래프
# --------------------------------------------------
st.divider()
st.subheader(
    f"📈 {month_names[selected_month]} 기온 예측 그래프"
)

fig = go.Figure()

# 실제 데이터
fig.add_trace(
    go.Scatter(
        x=X,
        y=y,
        mode="lines+markers",
        name="실제 기온",
        line=dict(color="#2196F3", width=3),
        marker=dict(size=7)
    )
)

# 선택한 알고리즘의 예측선
fig.add_trace(
    go.Scatter(
        x=graph_years,
        y=graph_values,
        mode="lines",
        name=f"{selected_model} 예측선",
        line=dict(color="#32CD32", width=3, dash="dash")
    )
)

# 미래 예측 지점
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
    title=f"{month_names[selected_month]} 월별 기온 예측",
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


# --------------------------------------------------
# 10. 알고리즘별 예측 결과 비교
# --------------------------------------------------
st.divider()
st.subheader("📊 세 가지 알고리즘 예측 결과 비교")

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
            f"{v:.1f}℃"
            for v in comparison_df["예측 기온(℃)"]
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


# --------------------------------------------------
# 11. 알고리즘 설명
# --------------------------------------------------
st.divider()
st.subheader("💡 회귀 알고리즘 알아보기")

with st.expander("1. 선형회귀"):
    st.write("""
    - 과거 데이터의 전체적인 직선 추세를 분석합니다.
    - 기온이 시간이 지나면서 일정하게 증가하거나 감소하는 경향을 예측합니다.
    - 계산이 간단하고 결과를 이해하기 쉽습니다.
    """)

with st.expander("2. 다항회귀"):
    st.write("""
    - 곡선 형태의 추세를 분석하는 방법입니다.
    - 기온의 증가와 감소가 일정하지 않은 경우에도 곡선으로 표현할 수 있습니다.
    - 먼 미래를 예측할 때 결과가 크게 달라질 수 있습니다.
    """)

with st.expander("3. 랜덤포레스트"):
    st.write("""
    - 여러 개의 의사결정나무를 조합하는 알고리즘입니다.
    - 복잡한 데이터 패턴을 학습할 수 있습니다.
    - 다만 학습한 연도 범위를 벗어난 미래 예측에는 한계가 있습니다.
    """)


st.info(
    "참고: 이 결과는 과거 기온 데이터에 기반한 통계적 예측입니다. "
    "실제 미래 날씨를 보장하는 일기예보는 아닙니다."
)
