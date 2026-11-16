
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier


# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="붓꽃 품종 예측 AI",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 AI")
st.write(
    "꽃의 크기를 입력하고 3가지 인공지능 알고리즘으로 "
    "붓꽃 품종을 예측해 보세요!"
)

st.divider()


# ==========================================
# 2. CSV 파일 불러오기
# ==========================================
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

    df.columns = df.columns.str.strip()

except Exception as e:
    st.error(f"CSV 파일을 읽을 수 없습니다: {e}")
    st.stop()


# ==========================================
# 3. 데이터 전처리
# ==========================================

# 원본 데이터의 오타를 표준 이름으로 변경
df = df.rename(columns={
    "꽃받임 너비": "꽃받침 너비"
})

features = [
    "꽃받침 길이",
    "꽃받침 너비",
    "꽃잎 길이",
    "꽃잎 너비"
]

target = "품종"

required_columns = features + [target]

if not all(col in df.columns for col in required_columns):
    st.error(
        "CSV 파일의 열 이름이 예상한 형식과 다릅니다.\n\n"
        f"현재 열 이름: {df.columns.tolist()}"
    )
    st.stop()

for col in features:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=required_columns).copy()

if df.empty:
    st.error("분석할 데이터가 없습니다.")
    st.stop()

X_all = df[features]
y = df[target]


# ==========================================
# 4. 알고리즘 3개 생성
# ==========================================

def make_models():

    models = {

        "① KNN (최근접 이웃)": Pipeline([
            ("scaler", StandardScaler()),
            ("model", KNeighborsClassifier(n_neighbors=5))
        ]),

        "② 의사결정나무": DecisionTreeClassifier(
            max_depth=4,
            random_state=42
        ),

        "③ 랜덤 포레스트": RandomForestClassifier(
            n_estimators=100,
            max_depth=4,
            random_state=42
        )
    }

    return models


# ==========================================
# 5. 알고리즘 작동 원리 설명
# ==========================================

explanations = {

    "① KNN (최근접 이웃)": """
    **KNN (K-Nearest Neighbors)**

    사용자가 입력한 꽃의 크기와 가장 가까운 기존 꽃 5개를 찾습니다.

    주변 5개 꽃 중 가장 많이 나타나는 품종을 예측 결과로 선택합니다.

    - 특징: 주변 데이터와의 거리를 이용합니다.
    - 장점: 원리를 이해하기 쉽고 직관적입니다.
    - 주의점: 데이터의 크기와 단위에 영향을 받기 때문에
      StandardScaler로 표준화합니다.
    """,

    "② 의사결정나무": """
    **Decision Tree (의사결정나무)**

    꽃의 길이와 너비를 여러 조건으로 나누어 품종을 구분합니다.

    예를 들어 꽃잎 길이가 특정 값보다 큰지 작은지 등을
    차례로 판단하여 최종 품종을 결정합니다.

    - 특징: 조건에 따라 가지가 나뉘는 구조입니다.
    - 장점: 예측 과정을 이해하기 쉽습니다.
    - 주의점: 학습 데이터에 지나치게 맞춰질 수 있습니다.
    """,

    "③ 랜덤 포레스트": """
    **Random Forest (랜덤 포레스트)**

    여러 개의 의사결정나무를 만들고 각각의 예측 결과를 종합합니다.

    여러 나무가 투표하는 방식으로 최종 품종을 결정합니다.

    - 특징: 여러 의사결정나무를 결합합니다.
    - 장점: 하나의 나무보다 안정적인 예측을 기대할 수 있습니다.
    - 주의점: 하나의 의사결정나무보다 작동 과정을 이해하기 어렵습니다.
    """
}


# ==========================================
# 6. 공통 예측 및 그래프 함수
# ==========================================

def run_prediction(
    selected_features,
    input_values,
    tab_name
):

    st.divider()

    st.subheader("🤖 3가지 알고리즘 예측 결과")

    X = df[selected_features]

    input_data = pd.DataFrame(
        [input_values],
        columns=selected_features
    )

    models = make_models()

    results = []

    # 세 알고리즘 학습 및 예측
    for name, model in models.items():

        model.fit(X, y)

        prediction = model.predict(input_data)[0]

        results.append({
            "알고리즘": name,
            "예측 품종": prediction
        })

    # 결과 표
    result_df = pd.DataFrame(results)

    st.dataframe(
        result_df,
        use_container_width=True,
        hide_index=True
    )

    # 세 알고리즘의 예측 일치 여부
    predictions = [r["예측 품종"] for r in results]

    if len(set(predictions)) == 1:

        st.success(
            f"🎉 세 알고리즘 모두 {predictions[0]}으로 예측했습니다!"
        )

    else:

        st.warning(
            "알고리즘별 예측 결과가 서로 다릅니다. "
            "각 알고리즘의 특성을 비교해 보세요."
        )

    # 첫 번째 알고리즘의 결과를 대표 결과로 강조
    st.markdown("### 🌸 알고리즘별 예측 결과")

    result_cols = st.columns(3)

    for i, result in enumerate(results):

        with result_cols[i]:

            st.markdown(f"**{result['알고리즘']}**")

            st.success(result["예측 품종"])

    # ======================================
    # 7. 그래프
    # ======================================

    st.divider()

    st.subheader("📊 붓꽃 데이터 분포 그래프")

    x_feature = selected_features[0]
    y_feature = selected_features[1]

    fig, ax = plt.subplots(figsize=(10, 6))

    species_colors = {
        "Iris-setosa": "#FF6384",
        "Iris-versicolor": "#36A2EB",
        "Iris-virginica": "#FFC857"
    }

    # 기존 붓꽃 데이터 표시
    for species in sorted(df[target].unique()):

        subset = df[df[target] == species]

        ax.scatter(
            subset[x_feature],
            subset[y_feature],
            color=species_colors.get(species, "#AAAAAA"),
            label=species,
            alpha=0.75,
            s=55
        )

    # 사용자가 입력한 위치
    ax.scatter(
        input_values[0],
        input_values[1],
        marker="*",
        s=650,
        color="#39FF14",
        edgecolors="black",
        linewidths=1.2,
        label="MY INPUT",
        zorder=10
    )

    ax.annotate(
        "MY INPUT ★",
        (input_values[0], input_values[1]),
        xytext=(10, 12),
        textcoords="offset points",
        color="#39FF14",
        fontsize=12,
        fontweight="bold"
    )

    ax.set_title(
        f"Iris Data - {tab_name}",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_xlabel(f"{x_feature} (cm)", fontsize=12)
    ax.set_ylabel(f"{y_feature} (cm)", fontsize=12)

    ax.set_xlim(
        df[x_feature].min() - 0.3,
        df[x_feature].max() + 0.3
    )

    ax.set_ylim(
        df[y_feature].min() - 0.2,
        df[y_feature].max() + 0.2
    )

    ax.grid(alpha=0.25)
    ax.legend()

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    st.caption(
        "★ 네온 초록색 별표는 사용자가 입력한 꽃의 위치입니다."
    )

    # ======================================
    # 8. 알고리즘 작동 원리
    # ======================================

    st.divider()

    st.subheader("🧠 알고리즘별 작동 원리")

    st.write(
        "이번 예측에 사용된 세 가지 알고리즘의 작동 방식을 알아봅시다."
    )

    for name, explanation in explanations.items():

        with st.expander(name):

            st.markdown(explanation)


# ==========================================
# 9. 탭 구성
# ==========================================

tab1, tab2 = st.tabs([
    "🌸 TAB 1. 꽃잎으로 예측하기",
    "🌿 TAB 2. 원하는 속성 2개로 예측하기"
])


# ==========================================
# TAB 1. 꽃잎 길이 + 꽃잎 너비
# ==========================================

with tab1:

    st.header("🌸 꽃잎 크기로 품종 예측하기")

    st.write(
        "꽃잎 길이와 꽃잎 너비를 입력하면 "
        "3가지 알고리즘이 품종을 예측합니다."
    )

    selected_features = [
        "꽃잎 길이",
        "꽃잎 너비"
    ]

    col1, col2 = st.columns(2)

    with col1:

        min_value = float(df["꽃잎 길이"].min())
        max_value = float(df["꽃잎 길이"].max())

        petal_length = st.number_input(
            "🌿 꽃잎 길이 (cm)",
            min_value=min_value,
            max_value=max_value,
            value=3.8,
            step=0.1,
            key="petal_length"
        )

        st.caption(
            f"입력 범위: {min_value} ~ {max_value} cm"
        )

    with col2:

        min_value = float(df["꽃잎 너비"].min())
        max_value = float(df["꽃잎 너비"].max())

        petal_width = st.number_input(
            "🌿 꽃잎 너비 (cm)",
            min_value=min_value,
            max_value=max_value,
            value=1.2,
            step=0.1,
            key="petal_width"
        )

        st.caption(
            f"입력 범위: {min_value} ~ {max_value} cm"
        )

    if st.button(
        "🔍 꽃잎으로 품종 예측하기",
        use_container_width=True,
        key="predict_petal"
    ):

        run_prediction(
            selected_features,
            [petal_length, petal_width],
            "Petal Analysis"
        )


# ==========================================
# TAB 2. 사용자가 속성 2개 선택
# ==========================================

with tab2:

    st.header("🌿 원하는 속성 2개로 품종 예측하기")

    st.write(
        "네 가지 속성 중 원하는 두 가지를 선택해 보세요."
    )

    st.info(
        "💡 기본 선택은 꽃받침 길이와 꽃받침 너비입니다. "
        "다른 속성 조합도 선택할 수 있습니다."
    )

    col1, col2 = st.columns(2)

    with col1:

        feature1 = st.selectbox(
            "첫 번째 분석 속성",
            features,
            index=0,
            key="feature1"
        )

    with col2:

        # 첫 번째 선택과 겹치지 않도록 설정
        second_options = [
            f for f in features if f != feature1
        ]

        default_second = (
            "꽃받침 너비"
            if "꽃받침 너비" in second_options
            else second_options[0]
        )

        second_index = second_options.index(default_second)

        feature2 = st.selectbox(
            "두 번째 분석 속성",
            second_options,
            index=second_index,
            key="feature2"
        )

    selected_features2 = [
        feature1,
        feature2
    ]

    st.divider()

    st.subheader("✏️ 선택한 속성의 측정값 입력")

    col1, col2 = st.columns(2)

    with col1:

        min1 = float(df[feature1].min())
        max1 = float(df[feature1].max())

        value1 = st.number_input(
            f"{feature1} (cm)",
            min_value=min1,
            max_value=max1,
            value=float(round((min1 + max1) / 2, 1)),
            step=0.1,
            key="value_feature1"
        )

        st.caption(
            f"입력 범위: {min1} ~ {max1} cm"
        )

    with col2:

        min2 = float(df[feature2].min())
        max2 = float(df[feature2].max())

        value2 = st.number_input(
            f"{feature2} (cm)",
            min_value=min2,
            max_value=max2,
            value=float(round((min2 + max2) / 2, 1)),
            step=0.1,
            key="value_feature2"
        )

        st.caption(
            f"입력 범위: {min2} ~ {max2} cm"
        )

    if st.button(
        "🔍 선택한 속성으로 품종 예측하기",
        use_container_width=True,
        key="predict_custom"
    ):

        run_prediction(
            selected_features2,
            [value1, value2],
            "Custom Feature Analysis"
        )


# ==========================================
# 10. 하단 데이터 안내
# ==========================================

st.divider()

with st.expander("📚 데이터 정보"):

    st.write("**전체 데이터 개수:**", len(df))

    st.write("**사용한 품종:**")

    st.write(
        ", ".join(sorted(df[target].unique()))
    )

    st.write("**품종별 데이터 개수**")

    st.dataframe(
        df[target].value_counts().rename("개수"),
        use_container_width=True
    )

    st.write("**원본 데이터 미리보기**")

    st.dataframe(
        df.head(10),
        use_container_width=True
    )

st.caption(
    "Iris 품종 예측 AI | KNN · Decision Tree · Random Forest"
)
