
import streamlit as st

# -----------------------------------------
# 1. 페이지 설정
# -----------------------------------------
st.set_page_config(
    page_title="MBTI 취향 탐험소",
    page_icon="🔎",
    layout="wide"
)

# -----------------------------------------
# 2. 디자인
# -----------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #F5F7FF;
}
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #5546A5;
    padding: 20px;
}
.sub-title {
    text-align: center;
    font-size: 18px;
    color: #777777;
}
.result-box {
    background-color: white;
    padding: 22px;
    border-radius: 15px;
    border: 1px solid #E2E3F5;
    margin-bottom: 15px;
}
.card-title {
    font-size: 22px;
    font-weight: bold;
    color: #51469A;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------
# 3. MBTI 유형 및 그룹
# -----------------------------------------
mbti_groups = {
    "INTJ": "NT", "INTP": "NT",
    "ENTJ": "NT", "ENTP": "NT",

    "INFJ": "NF", "INFP": "NF",
    "ENFJ": "NF", "ENFP": "NF",

    "ISTJ": "SJ", "ISFJ": "SJ",
    "ESTJ": "SJ", "ESFJ": "SJ",

    "ISTP": "SP", "ISFP": "SP",
    "ESTP": "SP", "ESFP": "SP"
}

group_info = {
    "NT": {
        "name": "🧠 분석가형",
        "description": "논리적이고 분석적인 사고를 즐기며 새로운 아이디어와 문제 해결에 관심이 많아요."
    },
    "NF": {
        "name": "🌱 외교관형",
        "description": "사람의 감정과 가치관을 중요하게 생각하고 창의적인 활동을 좋아해요."
    },
    "SJ": {
        "name": "📋 관리자형",
        "description": "책임감이 강하고 계획적으로 일을 처리하며 안정적인 환경을 선호해요."
    },
    "SP": {
        "name": "🎨 탐험가형",
        "description": "직접 경험하는 것을 좋아하고 자유롭고 활동적인 환경에서 능력을 발휘해요."
    }
}

# -----------------------------------------
# 4. 진로 데이터
# 연봉은 국내 직업의 참고용 예상 범위
# -----------------------------------------
careers = {
    "NT": [
        {
            "name": "💻 소프트웨어 개발자",
            "major": "컴퓨터공학과, 소프트웨어학과, 인공지능학과",
            "personality": "논리적으로 생각하고 문제를 해결하는 것을 좋아하며 새로운 기술을 배우는 사람",
            "salary": "약 4,000만~7,000만 원",
            "description": "컴퓨터 프로그램과 앱, 웹사이트 등을 개발하는 직업이에요."
        },
        {
            "name": "📊 데이터 분석가",
            "major": "통계학과, 데이터사이언스학과, 산업공학과",
            "personality": "숫자와 자료를 꼼꼼히 분석하고 숨겨진 규칙을 찾아내는 것을 좋아하는 사람",
            "salary": "약 3,800만~6,500만 원",
            "description": "다양한 데이터를 분석해 기업이나 사회의 의사결정을 돕는 직업이에요."
        }
    ],
    "NF": [
        {
            "name": "🧑‍⚕️ 심리상담 전문가",
            "major": "심리학과, 상담심리학과, 교육학과",
            "personality": "다른 사람의 이야기를 잘 들어주고 공감하며 사람의 마음에 관심이 많은 사람",
            "salary": "약 3,000만~5,000만 원",
            "description": "사람들의 고민을 듣고 정서적 성장과 문제 해결을 돕는 직업이에요."
        },
        {
            "name": "✍️ 콘텐츠 기획자",
            "major": "국어국문학과, 문예창작학과, 미디어커뮤니케이션학과",
            "personality": "상상력이 풍부하고 글쓰기와 새로운 아이디어를 만드는 것을 좋아하는 사람",
            "salary": "약 3,000만~5,500만 원",
            "description": "책, 영상, SNS 등 다양한 콘텐츠의 주제와 방향을 기획하는 직업이에요."
        }
    ],
    "SJ": [
        {
            "name": "👩‍🏫 교사",
            "major": "교육학과, 사범대학 관련 학과, 초등교육과",
            "personality": "책임감이 강하고 다른 사람에게 지식을 전달하는 것을 좋아하는 사람",
            "salary": "약 3,500만~6,500만 원",
            "description": "학생들에게 지식을 가르치고 성장과 학습을 돕는 직업이에요."
        },
        {
            "name": "🏛️ 공공행정 전문가",
            "major": "행정학과, 정책학과, 정치외교학과",
            "personality": "계획적이고 꼼꼼하며 사회 문제와 공공서비스에 관심이 많은 사람",
            "salary": "약 3,000만~5,000만 원",
            "description": "공공기관이나 행정기관에서 정책과 행정 업무를 수행하는 직업이에요."
        }
    ],
    "SP": [
        {
            "name": "🎨 UX/UI 디자이너",
            "major": "시각디자인학과, 산업디자인학과, 디지털미디어학과",
            "personality": "창의적이고 관찰력이 좋으며 새로운 디자인을 직접 만들어 보는 것을 좋아하는 사람",
            "salary": "약 3,500만~6,000만 원",
            "description": "사람들이 편리하게 사용할 수 있도록 앱과 웹사이트의 화면을 디자인하는 직업이에요."
        },
        {
            "name": "🎥 영상 콘텐츠 제작자",
            "major": "영상학과, 영화영상학과, 미디어학과",
            "personality": "활동적이고 표현력이 풍부하며 촬영과 편집 등 직접 만드는 일을 좋아하는 사람",
            "salary": "약 3,000만~5,500만 원",
            "description": "유튜브, 광고, 방송 등 다양한 영상 콘텐츠를 제작하는 직업이에요."
        }
    ]
}

# -----------------------------------------
# 5. 책 추천 데이터
# 모두 한국 작가의 소설
# -----------------------------------------
books = {
    "NT": [
        {
            "title": "천 개의 파랑",
            "author": "천선란",
            "description": "과학기술과 인간, 생명의 의미를 생각하게 하는 SF 소설이에요."
        },
        {
            "title": "지구 끝의 온실",
            "author": "김초엽",
            "description": "미래의 지구와 인간의 생존, 과학과 희망을 다룬 SF 소설이에요."
        }
    ],
    "NF": [
        {
            "title": "아몬드",
            "author": "손원평",
            "description": "감정과 공감, 성장과 우정에 대해 생각해 볼 수 있는 소설이에요."
        },
        {
            "title": "페인트",
            "author": "이희영",
            "description": "가족과 관계, 선택의 의미를 청소년의 시선으로 풀어낸 소설이에요."
        }
    ],
    "SJ": [
        {
            "title": "완득이",
            "author": "김려령",
            "description": "성장과 가족, 우정을 유쾌하게 그려낸 청소년 소설이에요."
        },
        {
            "title": "시간을 파는 상점",
            "author": "김선영",
            "description": "시간과 선택, 사람 사이의 관계를 생각하게 하는 소설이에요."
        }
    ],
    "SP": [
        {
            "title": "위저드 베이커리",
            "author": "구병모",
            "description": "신비로운 빵집을 배경으로 선택과 책임을 다룬 판타지 소설이에요."
        },
        {
            "title": "체리새우: 비밀글입니다",
            "author": "황영미",
            "description": "친구 관계와 자기 자신을 찾아가는 청소년 성장 소설이에요."
        }
    ]
}

# -----------------------------------------
# 6. 영화 추천 데이터
# 모두 2010년 이후 개봉 영화
# -----------------------------------------
movies = {
    "NT": [
        {
            "title": "승리호",
            "year": 2021,
            "description": "우주를 배경으로 펼쳐지는 SF 영화! 미래 기술과 상상력이 돋보여요."
        },
        {
            "title": "잠",
            "year": 2023,
            "description": "일상 속 미스터리를 논리적으로 추리하며 감상할 수 있는 스릴러 영화예요."
        }
    ],
    "NF": [
        {
            "title": "벌새",
            "year": 2019,
            "description": "청소년의 성장과 감정, 가족과 관계를 섬세하게 담아낸 영화예요."
        },
        {
            "title": "리틀 포레스트",
            "year": 2018,
            "description": "자신의 삶을 돌아보고 자연 속에서 위로를 얻는 따뜻한 영화예요."
        }
    ],
    "SJ": [
        {
            "title": "국제시장",
            "year": 2014,
            "description": "가족을 위한 책임과 희생, 우리 사회의 역사를 다룬 영화예요."
        },
        {
            "title": "택시운전사",
            "year": 2017,
            "description": "역사적 사건 속에서 용기와 책임의 의미를 생각하게 하는 영화예요."
        }
    ],
    "SP": [
        {
            "title": "극한직업",
            "year": 2019,
            "description": "개성 있는 캐릭터들과 빠른 전개가 돋보이는 코미디 영화예요."
        },
        {
            "title": "엑시트",
            "year": 2019,
            "description": "위기 상황에서 기지를 발휘하는 인물들의 활약을 담은 영화예요."
        }
    ]
}

# -----------------------------------------
# 7. 메인 화면
# -----------------------------------------
st.markdown(
    '<div class="main-title">🔎 MBTI 취향 탐험소</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">나의 MBTI로 알아보는 진로 · 책 · 영화 추천!</div>',
    unsafe_allow_html=True
)

st.write("")
st.info("✨ 나의 MBTI를 선택하고 나에게 어울리는 다양한 추천을 만나보세요!")

# MBTI 선택
mbti_list = [
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP"
]

selected_mbti = st.selectbox(
    "🧩 나의 MBTI를 선택해주세요!",
    mbti_list,
    index=0
)

# -----------------------------------------
# 8. 결과 출력
# -----------------------------------------
if st.button("🚀 나의 맞춤 추천 확인하기", use_container_width=True):

    group = mbti_groups[selected_mbti]

    st.balloons()

    st.markdown("---")

    st.markdown(
        f"<h2 style='text-align:center;color:#5546A5;'>"
        f"✨ {selected_mbti} 유형의 추천 결과 ✨</h2>",
        unsafe_allow_html=True
    )

    # MBTI 성향
    st.subheader(group_info[group]["name"])
    st.write(group_info[group]["description"])

    # -------------------------------------
    # 진로 추천
    # -------------------------------------
    st.markdown("---")
    st.header("💼 나에게 어울리는 진로 TOP 2")

    for i, career in enumerate(careers[group], 1):

        st.markdown(
            f'<div class="result-box">'
            f'<div class="card-title">{i}. {career["name"]}</div>'
            f'<p>{career["description"]}</p>'
            f'<b>🎓 관련 학과</b><br>{career["major"]}<br><br>'
            f'<b>💡 적합한 성격</b><br>{career["personality"]}<br><br>'
            f'<b>💰 예상 연봉 범위</b><br>{career["salary"]}'
            f'</div>',
            unsafe_allow_html=True
        )

    st.caption(
        "※ 연봉은 국내 취업시장의 참고용 추정 범위이며, "
        "경력·기업 규모·지역·고용 형태에 따라 달라질 수 있어요."
    )

    # -------------------------------------
    # 책 추천
    # -------------------------------------
    st.markdown("---")
    st.header("📚 나의 취향 저격 한국 소설 2권")

    col1, col2 = st.columns(2)

    for i, book in enumerate(books[group]):
        with [col1, col2][i]:
            st.markdown(
                f'<div class="result-box">'
                f'<div class="card-title">📖 {book["title"]}</div>'
                f'<b>✍️ 작가</b>: {book["author"]}<br><br>'
                f'{book["description"]}'
                f'</div>',
                unsafe_allow_html=True
            )

    # -------------------------------------
    # 영화 추천
    # -------------------------------------
    st.markdown("---")
    st.header("🎬 주말에 보기 좋은 영화 2편")

    col3, col4 = st.columns(2)

    for i, movie in enumerate(movies[group]):
        with [col3, col4][i]:
            st.markdown(
                f'<div class="result-box">'
                f'<div class="card-title">🍿 {movie["title"]}</div>'
                f'<b>📅 개봉 연도</b>: {movie["year"]}년<br><br>'
                f'{movie["description"]}'
                f'</div>',
                unsafe_allow_html=True
            )

    # -------------------------------------
    # 마무리
    # -------------------------------------
    st.markdown("---")

    st.success(
        "🎉 추천 결과를 확인했어요! "
        "책과 영화를 즐기면서 나의 관심 분야도 찾아보세요."
    )

    st.caption(
        "MBTI 추천은 재미와 자기 탐색을 위한 참고 자료입니다. "
        "실제 진로는 흥미, 적성, 경험과 다양한 가능성을 함께 고려해 보세요."
    )

st.markdown("---")

st.markdown(
    "<p style='text-align:center;color:gray;'>"
    "🔎 MBTI 취향 탐험소 | 나의 가능성을 발견하는 시간"
    "</p>",
    unsafe_allow_html=True
)
