
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# --------------------------------------------------
# 1. 페이지 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온분석")
st.write("원하는 월을 선택하면 연도별 최고기온과 최저기온을 비교합니다.")

# --------------------------------------------------
# 2. CSV 파일 경로 설정
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "temperature.csv"

# --------------------------------------------------
# 3. CSV 파일 읽기 (한글 인코딩 처리)
# --------------------------------------------------
try:
    if not CSV_PATH.exists():
        st.error(f"데이터 파일을 찾을 수 없습니다: {CSV_PATH}")
        st.stop()

    df = None

    for encoding in ["cp949", "euc-kr", "utf-8-sig"]:
        try:
            df = pd.read_csv(
                CSV_PATH,
                encoding=encoding
            )
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        st.error("CSV 파일의 인코딩을 확인해주세요.")
        st.stop()

except Exception as e:
    st.error(f"데이터 파일을 읽는 중 오류가 발생했습니다: {e}")
    st.stop()

# --------------------------------------------------
# 4. 필요한 컬럼 확인
# --------------------------------------------------
required_columns = [
    "일시",
    "최고기온(℃)",
    "최저기온(℃)"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(f"CSV에 필요한 컬럼이 없습니다: {missing_columns}")
    st.stop()

# --------------------------------------------------
# 5. 날짜 데이터 분석
# --------------------------------------------------

# 영문 월을 숫자로 변환
month_dict = {
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

# 2자리 연도를 실제 연도로 복원
# 첫 번째 데이터 Oct-07은 1907년으로 해석
years = []
months = []

previous_year = None

for date_value in df["일시"]:

    try:
        month_text, year_text = str(date_value).strip().split("-")

        month = month_dict[month_text[:3]]
        year_suffix = int(year_text)

        if previous_year is None:
            year = 1900 + year_suffix
        else:
            year = (previous_year // 100) * 100 + year_suffix

            if year < previous_year:
                year += 100

        previous_year = year

        years.append(year)
        months.append(month)

    except (ValueError, KeyError):
        years.append(None)
        months.append(None)

df["연도"] = years
df["월"] = months

# --------------------------------------------------
# 6. 기온 데이터 숫자 변환
# --------------------------------------------------
df["최고기온(℃)"] = pd.to_numeric(
    df["최고기온(℃)"],
    errors="coerce"
)

df["최저기온(℃)"] = pd.to_numeric(
    df["최저기온(℃)"],
    errors="coerce"
)

# --------------------------------------------------
# 7. 월 선택 메뉴
# --------------------------------------------------
st.subheader("📅 분석할 월 선택")

selected_month = st.selectbox(
    "월을 선택하세요.",
    options=list(range(1, 13)),
    format_func=lambda x: f"{x}월",
    index=0
)

# --------------------------------------------------
# 8. 선택한 월의 데이터 추출
# --------------------------------------------------
chart_data = df[
    df["월"] == selected_month
].copy()

# 결측치 제거
chart_data = chart_data.dropna(
    subset=[
        "연도",
        "최고기온(℃)",
        "최저기온(℃)"
    ]
)

# 연도 순서대로 정렬
chart_data = chart_data.sort_values("연도")

# --------------------------------------------------
# 9. 꺾은선 그래프 생성
# --------------------------------------------------
if chart_data.empty:

    st.warning("선택한 월에 표시할 기온 데이터가 없습니다.")

else:

    fig = go.Figure()

    # 최고기온 - 쨍한 연두색
    fig.add_trace(
        go.Scatter(
            x=chart_data["연도"],
            y=chart_data["최고기온(℃)"],
            mode="lines+markers",
            name="최고기온",
            line=dict(
                color="#7CFC00",
                width=3
            ),
            marker=dict(
                size=6,
                color="#7CFC00"
            ),
            hovertemplate=(
                "%{x}년<br>"
                "최고기온: %{y:.1f}℃"
                "<extra></extra>"
            )
        )
    )

    # 최저기온 - 연한 연두색
    fig.add_trace(
        go.Scatter(
            x=chart_data["연도"],
            y=chart_data["최저기온(℃)"],
            mode="lines+markers",
            name="최저기온",
            line=dict(
                color="#D9FF9A",
                width=3
            ),
            marker=dict(
                size=6,
                color="#D9FF9A"
            ),
            hovertemplate=(
                "%{x}년<br>"
                "최저기온: %{y:.1f}℃"
                "<extra></extra>"
            )
        )
    )

    # 그래프 제목 및 축 설정
    fig.update_layout(
        title=dict(
            text="월별 기온분석",
            x=0.5,
            xanchor="center",
            font=dict(size=25)
        ),

        xaxis=dict(
            title="연도",
            showgrid=True,
            dtick=5
        ),

        yaxis=dict(
            title="온도 (℃)",
            showgrid=True
        ),

        legend=dict(
            title="범례",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),

        hovermode="x unified",
        template="plotly_white",
        height=600
    )

    # --------------------------------------------------
    # 10. 스트림릿 화면에 그래프 표시
    # --------------------------------------------------
    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        f"선택한 월: {selected_month}월 | "
        f"분석 데이터: {len(chart_data)}개 연도"
    )

# --------------------------------------------------
# 11. 데이터 확인용 표
# --------------------------------------------------
with st.expander("📋 선택한 월의 기온 데이터 확인"):

    if not chart_data.empty:

        display_data = chart_data[
            [
                "연도",
                "최고기온(℃)",
                "최저기온(℃)"
            ]
        ].copy()

        display_data["연도"] = (
            display_data["연도"].astype(int)
        )

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )

st.divider()

st.caption("🌱 월별 최고기온과 최저기온의 장기 변화를 비교하는 기온 분석 앱입니다.")
