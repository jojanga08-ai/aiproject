
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import re

# =====================================
# 1. 페이지 설정
# =====================================
st.set_page_config(
    page_title="서울시 인구 통계",
    page_icon="📊",
    layout="wide"
)

st.title("📊 서울시 연령대별 인구 통계")
st.write("행정구역과 연도를 선택하여 연령대별 인구를 분석해 보세요.")

# =====================================
# 2. CSV 파일 경로
# pages 폴더의 상위 폴더에 CSV 존재
# =====================================
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "populaton.csv"

# =====================================
# 3. CSV 데이터 불러오기
# =====================================
@st.cache_data
def load_data():

    encodings = ["cp949", "euc-kr", "utf-8-sig", "utf-8"]

    for encoding in encodings:
        try:
            data = pd.read_csv(
                CSV_PATH,
                encoding=encoding,
                dtype=str
            )
            break

        except UnicodeDecodeError:
            continue

    else:
        raise ValueError("CSV 한글 인코딩을 확인해 주세요.")

    # 숫자 데이터 쉼표 제거
    for col in data.columns[1:]:
        data[col] = pd.to_numeric(
            data[col]
            .astype(str)
            .str.replace(",", "", regex=False),
            errors="coerce"
        )

    return data


try:
    df = load_data()

except FileNotFoundError:
    st.error("populaton.csv 파일을 찾을 수 없습니다.")
    st.stop()

except Exception as e:
    st.error(f"데이터 읽기 오류: {e}")
    st.stop()


# =====================================
# 4. 행정구역 정리
# =====================================
df["행정구역명"] = (
    df["행정구역"]
    .astype(str)
    .str.replace(r"\s*\(\d+\)", "", regex=True)
    .str.strip()
)

districts = df["행정구역명"].dropna().tolist()

# =====================================
# 5. 연도 자동 추출
# =====================================
years = set()

for col in df.columns:
    match = re.match(r"^(\d{4})년_", str(col))

    if match:
        years.add(match.group(1))

years = sorted(years)

if not years:
    st.error("연도 정보를 찾을 수 없습니다.")
    st.stop()

# =====================================
# 6. 연령대 추출
# =====================================
age_list = [
    "0~9세",
    "10~19세",
    "20~29세",
    "30~39세",
    "40~49세",
    "50~59세",
    "60~69세",
    "70~79세",
    "80~89세",
    "90~99세",
    "100세 이상"
]

# =====================================
# 7. 선택 메뉴
# =====================================
st.subheader("🔍 분석 조건")

col1, col2, col3 = st.columns(3)

with col1:
    selected_district = st.selectbox(
        "🏙️ 행정구역",
        districts
    )

with col2:
    selected_gender = st.selectbox(
        "👤 성별",
        ["전체 (성별 구분 없음)"]
    )

with col3:
    selected_year = st.selectbox(
        "📅 연도",
        years,
        index=len(years) - 1
    )

# ★ 핵심 수정 부분
# 연도를 반드시 문자열로 변환
selected_year = str(selected_year)

st.info(
    "현재 데이터 파일에는 성별 구분이 없어 "
    "전체 인구만 조회할 수 있습니다."
)

# =====================================
# 8. 선택한 행정구역 찾기
# =====================================
selected_row = df[
    df["행정구역명"] == selected_district
]

if selected_row.empty:
    st.error("해당 행정구역의 데이터가 없습니다.")
    st.stop()

selected_row = selected_row.iloc[0]

# =====================================
# 9. 연령대별 인구 추출
# =====================================
x_values = []
y_values = []

for age in age_list:

    # 연도와 연령대 컬럼 이름 생성
    column_name = (
        f"{selected_year}년_거주자_{age}"
    )

    if column_name in df.columns:

        value = selected_row[column_name]

        if pd.notna(value):
            x_values.append(age)
            y_values.append(int(value))

if len(x_values) == 0:
    st.warning("선택한 연도의 인구 데이터가 없습니다.")
    st.stop()

# =====================================
# 10. 총인구 표시
# =====================================
total_col = f"{selected_year}년_거주자_총인구수"

if total_col in df.columns:

    total = selected_row[total_col]

    if pd.notna(total):

        st.metric(
            label=f"{selected_district} 총인구",
            value=f"{int(total):,}명"
        )

# =====================================
# 11. 꺾은선 그래프
# =====================================
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
            size=11,
            line=dict(
                color="#FFFFFF",
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

# =====================================
# 12. 그래프 디자인
# =====================================
fig.update_layout(

    height=600,

    plot_bgcolor="#111111",
    paper_bgcolor="#111111",

    font=dict(
        family="Malgun Gothic, Apple SD Gothic Neo, sans-serif",
        color="#FFFFFF",
        size=13
    ),

    xaxis=dict(
        title="연령대",
        type="category",
        showgrid=True,
        gridcolor="#555555",
        categoryorder="array",
        categoryarray=x_values
    ),

    yaxis=dict(
        title="인구수 (명)",
        showgrid=True,
        gridcolor="#555555",
        tickformat=",",
        dtick=100,
        rangemode="tozero"
    ),

    hovermode="x unified",

    showlegend=False,

    margin=dict(
        l=80,
        r=30,
        t=40,
        b=80
    )
)

# =====================================
# 13. 그래프 출력
# =====================================
st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================
# 14. 데이터 표
# =====================================
st.subheader("📋 연령대별 인구 상세 데이터")

result_df = pd.DataFrame({
    "연령대": x_values,
    "인구수": y_values
})

result_df["인구수"] = result_df["인구수"].apply(
    lambda x: f"{x:,}명"
)

st.dataframe(
    result_df,
    use_container_width=True,
    hide_index=True
)

# =====================================
# 15. 완료 메시지
# =====================================
st.success("인구 통계 분석이 완료되었습니다! 🎉")
