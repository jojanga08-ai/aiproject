
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import re

# --------------------------------
# 1. 페이지 기본 설정
# --------------------------------
st.set_page_config(
    page_title="서울시 인구 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📊 서울시 연령대별 인구 분석")
st.caption("행정구역과 연도별 인구 현황을 확인해 보세요.")

# --------------------------------
# 2. CSV 파일 경로 설정
# py 파일은 pages 폴더 안에 있고
# CSV는 상위 폴더에 있음
# --------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "populaton.csv"

# --------------------------------
# 3. CSV 파일 불러오기
# 한글 인코딩 처리
# --------------------------------
@st.cache_data
def load_data():

    try:
        df = pd.read_csv(
            CSV_PATH,
            encoding="cp949",
            dtype=str
        )

    except UnicodeDecodeError:
        df = pd.read_csv(
            CSV_PATH,
            encoding="euc-kr",
            dtype=str
        )

    # 숫자 쉼표 제거
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        )

    return df


try:
    df = load_data()

except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.info("populaton.csv가 프로젝트 상위 폴더에 있는지 확인하세요.")
    st.stop()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# --------------------------------
# 4. 행정구역 이름 정리
# --------------------------------
df["행정구역명"] = (
    df["행정구역"]
    .astype(str)
    .str.replace(r"\s*\(\d+\)", "", regex=True)
    .str.strip()
)

districts = df["행정구역명"].dropna().tolist()

# --------------------------------
# 5. 연도 목록 추출
# --------------------------------
years = sorted(
    set(
        re.findall(
            r"^(\d{4})년_",
            " ".join(df.columns)
        )
    )
)

# --------------------------------
# 6. 연령대 컬럼 추출
# --------------------------------
age_columns = []

for col in df.columns:

    match = re.search(
        r"_(\d+~\d+세|100세 이상)$",
        col
    )

    if match:
        age_columns.append((col, match.group(1)))


def age_sort_key(item):

    age = item[1]

    if age == "100세 이상":
        return 100

    return int(age.split("~")[0])


age_columns = sorted(age_columns, key=age_sort_key)

# --------------------------------
# 7. 사용자 선택 메뉴
# --------------------------------
st.subheader("🔎 분석 조건 선택")

col1, col2, col3 = st.columns(3)

with col1:
    selected_district = st.selectbox(
        "🏙️ 행정구역 선택",
        districts
    )

with col2:
    selected_gender = st.selectbox(
        "👤 성별 선택",
        ["전체 (성별 구분 없음)"]
    )

with col3:
    selected_year = st.selectbox(
        "📅 연도 선택",
        years,
        index=len(years) - 1
    )

st.info(
    "현재 CSV에는 성별 구분이 없으므로 "
    "전체 인구 데이터만 표시합니다."
)

# --------------------------------
# 8. 선택한 지역 데이터 추출
# --------------------------------
selected_data = df[
    df["행정구역명"] == selected_district
]

if selected_data.empty:
    st.error("선택한 행정구역의 데이터가 없습니다.")
    st.stop()

selected_data = selected_data.iloc[0]

# --------------------------------
# 9. 선택한 연도의 연령대별 인구 추출
# --------------------------------
x_values = []
y_values = []

for col, age in age_columns:

    if col.startswith(selected_year + "년_"):

        value = selected_data[col]

        if pd.notna(value):
            x_values.append(age)
            y_values.append(int(value))

if not x_values:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    st.stop()

# --------------------------------
# 10. 주요 인구 정보
# --------------------------------
total_population_col = (
    selected_year + "년_거주자_총인구수"
)

if total_population_col in df.columns:
    total_population = selected_data[total_population_col]

    if pd.notna(total_population):
        st.metric(
            label=f"{selected_district} {selected_year}년 총인구",
            value=f"{int(total_population):,}명"
        )

# --------------------------------
# 11. 꺾은선 그래프
# --------------------------------
st.subheader(
    f"📈 {selected_district} {selected_year}년 연령대별 인구"
)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=x_values,
        y=y_values,
        mode="lines+markers",
        name="인구수",
        line=dict(
            color="#39FF14",
            width=4
        ),
        marker=dict(
            color="#39FF14",
            size=10,
            line=dict(
                color="#1B5E20",
                width=1
            )
        ),
        hovertemplate=(
            "연령대: %{x}<br>"
            "인구수: %{y:,}명"
            "<extra></extra>"
        )
    )
)

# --------------------------------
# 12. 그래프 디자인
# --------------------------------
fig.update_layout(

    height=550,

    plot_bgcolor="#111111",
    paper_bgcolor="#111111",

    font=dict(
        family="Malgun Gothic, Apple SD Gothic Neo, sans-serif",
        color="white",
        size=13
    ),

    xaxis=dict(
        title="연령대",
        type="category",
        showgrid=True,
        gridcolor="#444444",
        gridwidth=1,
        tickangle=0,
        categoryorder="array",
        categoryarray=x_values
    ),

    yaxis=dict(
        title="인구수 (명)",
        showgrid=True,
        gridcolor="#555555",
        gridwidth=1,
        tickformat=",",
        dtick=100,
        rangemode="tozero"
    ),

    margin=dict(
        l=70,
        r=30,
        t=40,
        b=70
    ),

    hovermode="x unified",

    showlegend=False
)

# --------------------------------
# 13. 그래프 출력
# --------------------------------
st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------
# 14. 데이터 표 출력
# --------------------------------
st.subheader("📋 연령대별 인구 데이터")

result_df = pd.DataFrame({
    "연령대": x_values,
    "인구수": y_values
})

result_df["인구수"] = result_df["인구수"].map(
    lambda x: f"{x:,}명"
)

st.dataframe(
    result_df,
    use_container_width=True,
    hide_index=True
)

st.success("인구 데이터 분석이 완료되었습니다! 🎉")
