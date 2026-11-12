
@st.cache_data
def load_data():
    if not FILE_PATH.exists():
        raise FileNotFoundError(
            f"CSV 파일을 찾을 수 없습니다: {FILE_PATH}"
        )

    # CSV 인코딩 자동으로 순서대로 확인
    encodings = ["utf-8-sig", "cp949", "euc-kr"]

    df = None

    for encoding in encodings:
        try:
            df = pd.read_csv(
                FILE_PATH,
                encoding=encoding
            )
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError(
            "CSV 파일의 인코딩을 확인할 수 없습니다. "
            "UTF-8 또는 CP949 형식으로 저장해 주세요."
        )

    required_columns = [
        "일시",
        "평균기온(℃)",
        "평균최고기온(℃)",
        "최고기온(℃)",
        "평균최저기온(℃)"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"CSV 파일에 필요한 열이 없습니다: {missing}"
        )

    # 날짜 변환
    df["날짜"] = pd.to_datetime(
        df["일시"].astype(str).str.strip(),
        format="%b-%y",
        errors="coerce"
    )

    # 기온 데이터 숫자로 변환
    for col in required_columns[1:]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = df.dropna(subset=["날짜"])

    df["연도"] = df["날짜"].dt.year
    df["월"] = df["날짜"].dt.month

    return df.sort_values("날짜")
