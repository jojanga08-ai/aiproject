
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# ---------------------------------
# 1. 페이지 기본 설정
# ---------------------------------
st.set_page_config(
    page_title="붓꽃 품종 예측 AI",
    page_icon="🌸",
    layout="wide"
)

# ---------------------------------
# 2. 제목
# ---------------------------------
st.title("🌸 붓꽃 품종 예측 AI")
st.write("꽃잎의 길이와 너비를 입력하면 AI가 붓꽃 품종을 예측합니다.")

st.divider()

# ---------------------------------
# 3. CSV 파일 불러오기
# ---------------------------------
current_dir = Path(__file__).resolve().parent

possible_paths = [
    current_dir.parent / "Iris.csv",
    current_dir / "Iris.csv",
    Path.cwd() / "Iris.csv"
]

file_path = next(
    (p for p in possible_paths if p.exists()),
    None
)

if file_path is None:
    st.error("Iris.csv 파일을 찾을 수 없습니다.")
    st.stop()

try:
    try:
        df = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8-sig")

    # 열 이름의 앞뒤 공백 제거
    df.columns = df.columns.str.strip()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# ---------------------------------
# 4. 데이터 전처리
# ---------------------------------
required_columns = ["꽃잎 길이", "꽃잎 너비", "품종"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름을 확인해주세요.")
    st.stop()

df = df[required_columns].dropna()

X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

# ---------------------------------
# 5. KNN 모델 만들기
# ---------------------------------
model = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier(n_neighbors=5))
])

model.fit(X, y)

# ---------------------------------
# 6. 입력 가능한 범위 계산
# ---------------------------------
min_length = float(df["꽃잎 길이"].min())
max_length = float(df["꽃잎 길이"].max())

min_width = float(df["꽃잎 너비"].min())
max_width = float(df["꽃잎 너비"].max())

# ---------------------------------
# 7. 사용자 입력
# ---------------------------------
st.subheader("✏️ 꽃잎 크기 입력")

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "🌿 꽃잎 길이 (cm)",
        min_value=min_length,
        max_value=max_length,
        value=3.8,
        step=0.1,
        format="%.1f"
    )

    st.caption(
        f"입력 가능 범위: {min_length} ~ {max_length} cm"
    )

with col2:
    petal_width = st.number_input(
        "🌿 꽃잎 너비 (cm)",
        min_value=min_width,
        max_value=max_width,
        value=1.2,
        step=0.1,
        format="%.1f"
    )

    st.caption(
        f"입력 가능 범위: {min_width} ~ {max_width} cm"
    )

st.divider()

# ---------------------------------
# 8. 품종 예측
# ---------------------------------
if st.button("🔍 붓꽃 품종 예측하기", use_container_width=True):

    input_data = pd.DataFrame(
        [[petal_length, petal_width]],
        columns=["꽃잎 길이", "꽃잎 너비"]
    )

    prediction = model.predict(input_data)[0]

    st.success("AI 예측이 완료되었습니다!")

    st.subheader("🌸 예측 결과")

    st.markdown(
        f"## 🌺 {prediction}"
    )

    st.write(
        f"꽃잎 길이: **{petal_length:.1f} cm**"
    )

    st.write(
        f"꽃잎 너비: **{petal_width:.1f} cm**"
    )

    # ---------------------------------
    # 9. 그래프 그리기
    # ---------------------------------
    st.subheader("📊 붓꽃 크기 분포 그래프")

    fig, ax = plt.subplots(figsize=(10, 6))

    # 품종별 기존 데이터 표시
    colors = {
        "Iris-setosa": "#FF6384",
        "Iris-versicolor": "#36A2EB",
        "Iris-virginica": "#FFC857"
    }

    for species in sorted(df["품종"].unique()):

        subset = df[df["품종"] == species]

        ax.scatter(
            subset["꽃잎 길이"],
            subset["꽃잎 너비"],
            color=colors.get(species, "#AAAAAA"),
            label=species,
            alpha=0.7,
            s=55
        )

    # 사용자가 입력한 데이터: 네온 초록색 별
    ax.scatter(
        petal_length,
        petal_width,
        marker="*",
        s=500,
        color="#39FF14",
        edgecolors="black",
        linewidths=1.2,
        label="My Input",
        zorder=10
    )

    # 입력값 표시
    ax.annotate(
        "MY INPUT ★",
        (petal_length, petal_width),
        xytext=(10, 12),
        textcoords="offset points",
        color="#39FF14",
        fontsize=11,
        fontweight="bold"
    )

    # 그래프 제목과 축
    ax.set_title(
        "Iris Petal Length & Width",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_xlabel("Petal Length (cm)", fontsize=12)
    ax.set_ylabel("Petal Width (cm)", fontsize=12)

    ax.set_xlim(min_length - 0.3, max_length + 0.3)
    ax.set_ylim(min_width - 0.2, max_width + 0.2)

    ax.grid(alpha=0.25)
    ax.legend()

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    st.info(
        "💡 네온 초록색 별표(★)가 사용자가 입력한 꽃의 위치입니다."
    )

# ---------------------------------
# 10. 데이터 안내
# ---------------------------------
st.divider()

with st.expander("📚 AI 모델 및 데이터 정보"):

    st.write("**사용한 알고리즘:** K-최근접 이웃(KNN)")
    st.write("**이웃 개수:** 5개")
    st.write("**데이터 표준화:** StandardScaler")
    st.write("**학습 데이터 수:**", len(df))
    st.write("**품종 종류:**", df["품종"].nunique())

    st.write("**품종별 데이터 개수**")
    st.dataframe(
        df["품종"].value_counts().rename("개수")
    )

    st.write("**사용한 데이터 미리보기**")
    st.dataframe(df.head(10))
