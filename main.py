import streamlit as st #스트림릿 페이지
import time
import pandas as pd
# import 대상 -> 파일(.py)
# from 파일 import 함수, 클래스 -> 해당 파일의 일부 함수/클래스만 임포트
from crawling import crawling_saramin, crawling_work24, download_to_csv

# 레이아웃(웹페이지의 생김새)
# 스트림릿 웹페이지의 '헤더'역할
st.set_page_config(page_title = "채용공고 자동 크롤링 서비스",
                   layout = 'wide')

st.title("채용 공고 조회 서비스")
st.write("""이 서비스는 채용 공고를 조회하기 위해 만든 서비스 입니다.
            \n사람인과 고용24 페이지에 검색어를 입력하여 자동으로 공고를 크롤링합니다.
            \n크롤링한 내용은 하단의 표에서 확인 가능하며 csv파일로 다운로드할 수 있습니다."""
)

# 공고를 조회할 사이트를 선택
site_select = st.radio("크롤링할 사이트 선택", ['사람인(Saramin)', '고용24(Work24)'], horizontal=True)

# with st.sidebar:
#   st.write('사이드 확장')

with st.expander("상세 검색 조건", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        search_text = st.text_input("검색어를 입력", placeholder='예 : 파이썬, 인공지능')

        except_text = st.text_input("제외할 검색어", placeholder='예 : 야간 근무, 출장')

        max_pages = st.number_input('크롤링할 페이지 수', min_value=1, max_value=30)

    with col2:
        if site_select == '사람인':
            # 사람인 사이트에서 '지역'을 의미하는 코드만 분리
            loc_options = {
                "전체": None,
                "서울": "101000",
                "경기": "102000",
                "인천": "108000",
                "부산": "106000",
                "대구": "104000",
                "광주": "103000",
                "대전": "105000"
            }

            selected_location = st.multiselect('지역을 선택하세요.', list(loc_options.keys()), default=['전체'])

            # st.write(selected_location)
            # 크롤링 진행할 때 사용하기 위해 문자열 추출
            # selected_location으로 '서울', '경기' 같은 '지역명' 추출
            # loc_oprionts(딕셔너리)이므로, loc_options['부산'] => 값
            # x는 '지역명'
            # if 조건이 붙는 이유 : '지역명' 없는 '지역'이라면 추가가 안됨.
            locations = [loc_options[x] for x in selected_location if loc_options[x]]

            # st.write(locations)

            # 직무 검색
            cat_options = {
                "전체": None,
                "IT개발·데이터": "2",
                "경영·사무": "3",
                "마케팅·홍보": "4",
                "디자인": "9",
                "영업": "5"
            }

            selected_category = st.multiselect( "직무를 선택하세요", list(cat_options.keys()), default=["IT개발·데이터"])
            category = [cat_options[x] for x in selected_category if cat_options[x]]

            # 경력
            career_options = {'전체':'0', '신입':'1', '경력':'2', '신입/경력':'3'}
            selected_career = st.selectbox('경력을 선택하세요', list(career_options.keys()))
            career = career_options[selected_career]

            # 학력
            edu_option = {"전체": "0", "고졸": "1", "대졸(2,3년)": "2", "대졸(4년)": "3", '석사':'4', '박사':'5'}
            selected_edu = st.selectbox('학력을 선택하세요', list(edu_option.keys()))
            edu = edu_option[selected_edu]

        else : # 고용24
            region = st.text_input('지역 코드를 입력하세요', value='11000')
            occupation = st.text_input('직종 코드를 입력하세요', value='024', help='직종 코드 제한')

            # 경력
            career_options = {"전체": "A", "신입": "N", "경력": "E", "관계없음": "Z"}
            career = st.selectbox('경력을 선택하세요', list(career_options.keys()))
            career = career_options[career]
            
            # 학력
            edu_options = {
                "전체": "noEdu",
                "중졸이하": "01,02",
                "고졸": "03",
                "대졸(2~3년)": "04",
                "대졸(4년)": "05",
                "석사": "06",
                "박사": "07",
                "학력무관": "00",
            }
            edu = st.selectbox('학력을 선택하세요', list(edu_options.keys()))
            edu = edu_options[edu]

# st.button(버튼에 들어갈 글자, '크기 조절 옵션')
crawling_clicked = st.button("크롤링 시작",
                             use_container_width=True,
                             type='primary')

# crawling_clicked -> True (버튼을 눌렀음) / False(버튼을 누르지 않았음)
if crawling_clicked:
    st.write("버튼을 누름")
else:
    st.write("버튼을 안누름")

# 크롤링 시행!
# 1. 크롤링한 결과를 어떻게 받아올 것인가?
df = pd.DataFrame()

if "df" not in st.session_state:
    st.session_state["df"] = pd.DataFrame()
    
# 2. 크롤링 하는동안 어떻게 안내할 것인가?
if crawling_clicked :
    # 2-1. 검색어나 필수요소가 누락된 경우 안내
    # 검색어(search_text) 누락된 경우(not)
    if not search_text :
        st.warning("검색어를 입력해주세요!")
    # 2-2. 크롤링 시행하는 동안 '기다려주세요' 라는 내용 표시
    else :
        with st.spinner(f"{site_select}에서 {search_text} 검색 결과 가져오는 중..."):
            time.sleep(10)
        if site_select == "사람인" :
            # 사람인 사이트의 내용을 크롤링하는 함수
            df = crawling_saramin(search_text = search_text,
                                  except_text = except_text,
                                  region = locations,
                                  category = category,
                                  career = career,
                                  education = edu,
                                  max_pages = max_pages)
            # pass
        else:  
            # 고용24 사이트의 내용을 크롤링하는 함수
            df = crawling_work24(
                    search_text = search_text,
                    except_text = except_text,
                    region = region,
                    category = occupation,
                    career = career,
                    education = edu,
                    max_pages = max_pages )
            # 크롤링
            
        st.session_state['df'] = df
# st.session_state가 뭘까?
# 화면을 렌더링할 때에도 데이터프레임의 정보를 기억하도록 만들어준다.
# session_state는 '딕셔너리'처럼 저장
# session_state['df']
# df = st.session_state[df]와 같은 표현

df = st.session_state.df

if not df.empty :
    st.subheader('검색 결과')
    st.dataframe(df, use_container_width=True, hide_index=True)

    csv_data = download_to_csv(df)
    st.download_button(label='CSV 결과 다운로드',
                       data=csv_data,
                       file_name = f'crawling_results_{site_select}.csv',
                       mime='text/csv')


# st.write(df)
