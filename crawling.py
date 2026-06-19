# 라이브러리 임포트
# 크롤링 : 인터넷에 있는 정보를 긁어옴
import requests                 #인터넷 주소(url)에 html 파일을 요청
from bs4 import BeautifulSoup   #그렇게 해서 얻어온 html 파일을 예쁘게 '파싱'(필요 정보 추출)
import pandas as pd             
import re                       #정규표현식(regular expression), 문자열 정제

# 검색어, 제외할 검색어, 지역, 직무, 경력, 학력, 페이지 수
# 매개변수에 입력될 자료형 '미리 안내'
# default 값

# url, header, parameters => requests.get(주소) 주소로 요청
# soup 객체로 파싱, 가지고 있다가 select(), select_one()으로 필요한 파트 추출
# 처음에 초기화 해놓은 rows에 append해서 최종적인 모양 만듦

def crawling_saramin(
    search_text: str ,
    except_text: str = "",
    region: list = None,
    category: list = None,
    career: str = "",
    education: str = "",
    max_pages: int = 1):

    # 결과로 반환할 데이터 프레임의 '열 이름'과 '행' 리스트
    columns =['이름','위치','조건1','조건2','회사이름','링크']
    rows = []

    # requests로 일단 '검색할 페이지'에 요청!
    url = "https://www.saramin.co.kr/zf_user/search"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
    }

    # 파라미터 정제 -> 여기서 파라미터는 '검색 조건'
    #'키'는 웹사이트에서 지정한 키
    parameters = {'searchword' : search_text,
                  'except_read': except_text,
                  'comp_page'  : max_pages
                  }

    # 직무
    if category :
        parameters['cat_mcd'] = category
    # 지역
    if region :
        parameters['loc_mcd'] = region
    # 경력
    if career :
        parameters['career_cd'] = career
    # 학력
    if education :
        parameters['edu_cd'] = education

    response = requests.get(url, headers=headers,
                            params=parameters,         #조건에 대한 정보
                            timeout=15         #html 반환해줄 때까지의 대기시간
                            )

    # 크롤링 결과를 response로 받고,
    # response 안에 있는 text 파일을 'html.parser'로 파싱
    # 객체 soup를 생성
    soup = BeautifulSoup(response.text, 'html.parser')

    # 내가 필요한 결과의 '구분자' 전달, 추출
    # soup.select(구분자) : '구분자'를 보유한 모든 내용
    # soup.select_one(구분자) : '구분자'를 보유한 내용 딱 하나
    items = soup.select('div.item_recruit')

    for item in items:
        job_area = item.select_one('div.area_job')
        corp_area = item.select_one("div.area_corp")

        # 직무 정보가 없다!
        if not job_area :
            # 한 칸의 정보가 없을 때에는 '이번에만 넘어가자'
            continue

        # 직무, 회사정보 get
        job_title = job_area.select_one('.job_tit').get_text(strip=True)
        condition_area = job_area.select_one('.job_condition')
        spans = condition_area.select('span')

        location = spans[0].get_text(strip=True)
        condition1 = spans[1].get_text(strip=True)

        # condition2 = spans[-1].get_text(strip=True)
        job_sector = item.select_one('div.job_sector')
        condition2 = job_sector.get_text(strip=True)

        # 회사 정보
        corp_name = corp_area.select_one('.corp_name').get_text(strip=True)

        # 링크
        link = job_area.select_one('.job_tit').select_one('.data_layer[href]')
        real_link = 'https://www.saramin.co.kr' + link.get('href')

        rows.append({
            '이름':job_title,
            '위치':location,
            '조건1':condition1,
            '조건2':condition2,
            '회사이름':corp_name,
            '링크':real_link
        })

    df = pd.DataFrame(rows)
    # print(df)

    return df


def crawling_work24(
                    search_text: str,
                    except_text: str = "",
                    region: list = None,
                    category: list = None,
                    career: str = "",
                    education: str = "",
                    max_pages: int = 1,
                    ):

    url = 'https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do'

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",}

    parameters = {'srcKeyword':search_text,
                  'notSrcKeyword':except_text,
                  'pageIndex':max_pages,
                  'resultCnt':10,
                  'CodeDepth1Info':region,
                  'occupation':"024", #IT개발 직무
                  'careerTypes':"",
                  'academicGbnoEdu':""}

    # 1.request
    response = requests.get(url,
                            headers=headers,
                            params=parameters, 
                            timeout=15)
    # 2.soup 파싱
    # 크롤링 결과를 response로 받고,
    # response 안에 있는 text 파일을 'html.parser'로 파싱
    # 객체 soup를 생성
    soup = BeautifulSoup(response.text, "html.parser")

    # 내가 필요한 결과의 '구분자' 전달, 추출
    # soup.select(구분자) : '구분자'를 보유한 모든 내용
    # soup.select_one(구분자) : '구분자'를 보유한 내용 딱 하나
    # items = soup.select("div.box_table_group.gap_box08.column")
    items = soup.select("td.al_left.pd24")
    items2 = soup.select("td.link.pd24")
    # print(items) #디버깅
    rows = []

    # for문 동시에 여러개 돌리기
    # for a, b in zip (a, b): -> a와 b가 같은 길이 여야함
    for item, item2 in zip(items, items2):
        # 3.이름, 위치, 조건1, 조건2, 회사이름, 링크 -> soup 파싱에서 추출

        job_area = item.select("div.box_table_group.gap_box08.column")
        cell = item.select("div.cell")
        money = item2.select_one("span.item.b1_sb").get_text(strip=True)
        # condition_area = item.select("td.link.pd24")

        # spans = condition_area.select('span')

        name = cell[1].get_text(strip=True)
        corp_name = cell[0].get_text(strip=True)
        # money = item2.select_one("li.dollar").get_text(strip=True)

        money = re.sub(r'\s+', '', money)
        work_time = item2.select_one("li.time")
        t = ''
        if work_time : 
            if len(work_time) > 1 :
                for i in range(len(work_time)):
                    t += work_time.select('span')[i].text
            elif len(work_time) == 1:
                t = work_time.select_one('span').text
            else :
                t = ''
        else:
            t = ''
        print(t)                
        #location = item2.select_one("li.site").get_text(strip=True)
        #link = cell[1].select_one("a.href")
        # real_link = "https://www.work24.go.kr" + link.get("href")
    # rows.append(
    #     {
    #         "이름": name,
    #         "위치": location,
    #         "근무시간": work_time,
    #         "연봉": money,
    #         "회사이름": corp_name,
    #         "링크" : link
    #     }
    # )

    # df = pd.DataFrame(rows)
    # print(df)
    # return "고용24 결과"


if __name__ == '__main__':
     crawling_work24('빅데이터')
