
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# --------------------------------
# 1. 페이지 설정
# --------------------------------
st.set_page_config(
    page_title="붓꽃 품종 예측 AI",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 AI")
st.write("꽃잎의 길이와 너비로 붓꽃의 품종을 예측해 보세요!")

st.divider()

# --------------------------------
# 2. CSV 파일 불러오기
# --------------------------------
current_dir = Path(__file__).resolve().parent

# pages 폴더의 상위 폴더에 있는 CSV
file_path = current_dir.parent / "Iris.csv"

if not file_path.exists():
    st.error("Iris.csv 파일을 찾을 수 없습니다.")
    st.stop()

try:
    try:
        df = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8-sig")

    # 열 이름 공백 제거
    df.columns = df.columns.str.strip()

except Exception as e:
    st.error(f"CSV 파일 오류: {e}")
    st.stop()

# --------------------------------
# 3. 데이터 확인 및 전처리
# --------------------------------
required_columns = ["꽃잎 길이", "꽃잎 너비", "품종"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름을 확인해주세요.")
    st.stop()

df = df[required_columns].copy()

df["꽃잎 길이"] = pd.to_numeric(
    df["꽃잎 길이"], errors="coerce"
)

df["꽃잎 너비"] = pd.to_numeric(
    df["꽃잎 너비"], errors="coerce"
)

df = df.dropna()

X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

# --------------------------------
# 4. 알고리즘 3개 만들기
# --------------------------------

models = {
    "① KNN (최근접 이웃)": Pipeline([
        ("scaler", StandardScaler()),
        ("model", KNeighborsClassifier(n_neighbors=5))
    ]),

    "② 의사결정나무": DecisionTreeClassifier(
        random_state=42
    ),

    "③ 랜덤 포레스트": RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )
}

# 모든 알고리즘 학습
for model in models.values():
    model.fit(X, y)

# --------------------------------
# 5. 입력 가능 범위
# --------------------------------
min_length = float(X["꽃잎 길이"].min())
max_length = float(X["꽃잎 길이"].max())

min_width = float(X["꽃잎 너비"].min())
max_width = float(X["꽃잎 너비"].max())

# --------------------------------
# 6. 사용자 입력
# --------------------------------
st.subheader("✏️ 꽃잎 크기 입력")

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "🌿 꽃잎 길이 (cm)",
        min_value=min_length,
        max_value=max_length,
        value=3.8,
        step=0.1
    )

    st.caption(
        f"입력 범위: {min_length} ~ {max_length} cm"
    )

with col2:
    petal_width = st.number_input(
        "🌿 꽃잎 너비 (cm)",
        min_value=min_width,
        max_value=max_width,
        value=1.2,
        step=0.1
    )

    st.caption(
        f"입력 범위: {min_width} ~ {max_width} cm"
    )

st.divider()

# --------------------------------
# 7. 알고리즘 선택
# --------------------------------
st.subheader("🤖 예측 알고리즘 선택")

selected_model = st.selectbox(
    "사용할 분류 알고리즘을 선택하세요.",
    list(models.keys())
)

st.caption(
    "총 3가지 알고리즘 중 하나를 선택할 수 있습니다."
)

# --------------------------------
# 8. 품종 예측 버튼
# --------------------------------
if st.button(
    "🔍 붓꽃 품종 예측하기",
    use_container_width=True
):

    input_data = pd.DataFrame(
        [[petal_length, petal_width]],
        columns=["꽃잎 길이", "꽃잎 너비"]
    )

    # 선택한 알고리즘 예측
    prediction = models[selected_model].predict(
        input_data
    )[0]

    st.success("AI 예측이 완료되었습니다!")

    st.subheader("🌸 예측 결과")

    st.markdown(f"## 🌺 {prediction}")

    st.write(f"사용 알고리즘: **{selected_model}**")
    st.write(f"꽃잎 길이: **{petal_length:.1f}cm**")
    st.write(f"꽃잎 너비: **{petal_width:.1f}cm**")

    st.divider()

    # --------------------------------
    # 9. 세 알고리즘 예측 결과 비교
    # --------------------------------
    st.subheader("🏆 알고리즘별 예측 결과 비교")

    comparison = []

    for name, model in models.items():

        result = model.predict(input_data)[0]

        comparison.append({
            "알고리즘": name,
            "예측 품종": result,
            "선택 여부": "⭐ 선택한 알고리즘"
            if name == selected_model else ""
        })

    comparison_df = pd.DataFrame(comparison)

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------
    # 10. 그래프
    # --------------------------------
    st.subheader("📊 붓꽃 크기 분포 그래프")

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = {
        "Iris-setosa": "#FF6384",
        "Iris-versicolor": "#36A2EB",
        "Iris-virginica": "#FFC857"
    }

    # 기존 데이터 표시
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

    # 사용자 입력값 네온 초록색 별표
    ax.scatter(
        petal_length,
        petal_width,
        marker="*",
        s=600,
        color="#39FF14",
        edgecolors="black",
        linewidths=1.2,
        label="MY INPUT",
        zorder=10
    )

    ax.annotate(
        "MY INPUT ★",
        (petal_length, petal_width),
        xytext=(10, 12),
        textcoords="offset points",
        color="#39FF14",
        fontsize=12,
        fontweight="bold"
    )

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
        "💡 네온 초록색 별표가 사용자가 입력한 꽃의 위치입니다."
    )

# --------------------------------
# 11. 데이터 및 알고리즘 안내
# --------------------------------
st.divider()

with st.expander("📚 데이터 및 알고리즘 정보"):

    st.write("**전체 데이터 개수:**", len(df))

    st.write("**사용한 알고리즘:**")
    st.write("1. KNN")
    st.write("2. 의사결정나무")
    st.write("3. 랜덤 포레스트")

    st.write("**품종별 데이터 개수**")

    st.dataframe(
        df["품종"].value_counts().rename("데이터 개수")
    )

    st.write("**데이터 미리보기**")
    st.dataframe(df.head(10))
