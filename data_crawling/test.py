from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from time import sleep
import random
import re

from selenium import webdriver
import sys

options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
options.add_argument('window-size=1380,900')
driver = webdriver.Chrome(options=options)

# 대기 시간
driver.implicitly_wait(time_to_wait=3)

# 반복 종료 조건
loop = True

URL = 'https://map.naver.com/p/search/%EA%B0%95%EB%82%A8%EA%B5%AC%20%EB%A7%9B%EC%A7%91?c=13.00,0,0,0,dh'
driver.get(url=URL)

def switch_left():
    ############## iframe으로 왼쪽 포커스 맞추기 ##############
    driver.switch_to.parent_frame()
    iframe = driver.find_element(By.XPATH,'//*[@id="searchIframe"]')
    driver.switch_to.frame(iframe)
    
def switch_right():
    ############## iframe으로 오른쪽 포커스 맞추기 ##############
    driver.switch_to.parent_frame()
    iframe = driver.find_element(By.XPATH,'//*[@id="entryIframe"]')
    driver.switch_to.frame(iframe)


while(True):
    switch_left()

    # 페이지 숫자를 초기에 체크 [ True / False ]
    # 이건 페이지 넘어갈때마다 계속 확인해줘야 함 (페이지 새로 로드 될때마다 버튼 상태 값이 바뀜)
    next_page = driver.find_element(By.XPATH,'//*[@id="app-root"]/div/div[3]/div[2]/a[7]').get_attribute('aria-disabled')
    
    if(next_page == 'true'):
        break

    ############## 맨 밑까지 스크롤 ##############
    scrollable_element = driver.find_element(By.CLASS_NAME, "Ryr1F")

    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element)

    while True:
        # 요소 내에서 아래로 600px 스크롤
        driver.execute_script("arguments[0].scrollTop += 600;", scrollable_element)

        # 페이지 로드를 기다림
        sleep(1)  # 동적 콘텐츠 로드 시간에 따라 조절

        # 새 높이 계산
        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element)

        # 스크롤이 더 이상 늘어나지 않으면 루프 종료
        if new_height == last_height:
            break

        last_height = new_height


    ############## 현재 page number 가져오기 - 1 페이지 ##############

    page_no = driver.find_element(By.XPATH,'//a[contains(@class, "mBN2s qxokY")]').text

    # 현재 페이지에 등록된 모든 가게 조회
    # 첫페이지 광고 2개 때문에 첫페이지는 앞 2개를 빼야함
    if(page_no == '1'):
        elemets = driver.find_elements(By.XPATH,'//*[@id="_pcmap_list_scroll_container"]//li')[2:]
    else:
        elemets = driver.find_elements(By.XPATH,'//*[@id="_pcmap_list_scroll_container"]//li')

    print('현재 ' + '\033[95m' + str(page_no) + '\033[0m' + ' 페이지 / '+ '총 ' + '\033[95m' + str(len(elemets)) + '\033[0m' + '개의 가게를 찾았습니다.\n')

    for index, e in enumerate(elemets, start=1):
        final_element = e.find_element(By.CLASS_NAME,'CHC5F').find_element(By.XPATH, ".//a/div/div/span")

        print(str(index) + ". " + final_element.text)

    print(Colors.RED + "-"*50 + Colors.RESET)

    switch_left()

    sleep(2)

    for index, e in enumerate(elemets, start=1):
        store_name = '' # 가게 이름
        category = '' # 카테고리
        new_open = '' # 새로 오픈
        
        rating = 0.0 # 평점
        visited_review = 0 # 방문자 리뷰
        blog_review = 0 # 블로그 리뷰
        store_id = '' # 가게 고유 번호
        
        address = '' # 가게 주소
        business_hours = [] # 영업 시간
        phone_num = '' # 전화번호

        switch_left()


        # 순서대로 값을 하나씩 클릭
        e.find_element(By.CLASS_NAME,'CHC5F').find_element(By.XPATH, ".//a/div/div/span").click()

        sleep(2)

        switch_right()

        ################### 여기부터 크롤링 시작 ##################
        title = driver.find_element(By.XPATH,'//div[@class="zD5Nm undefined"]')
        store_info = title.find_elements(By.XPATH,'//div[@class="YouOG DZucB"]/div/span')


        # 가게 이름
        store_name = title.find_element(By.XPATH,'.//div[1]/div[1]/span[1]').text

        # 카테고리
        category = title.find_element(By.XPATH,'.//div[1]/div[1]/span[2]').text

        if(len(store_info) > 2):
            # 새로 오픈
            new_open = title.find_element(By.XPATH,'.//div[1]/div[1]/span[3]').text


        ###############################

        review = title.find_elements(By.XPATH,'.//div[2]/span')

        # 인덱스 변수 값
        _index = 1

        # 리뷰 ROW의 갯수가 3개 이상일 경우 [별점, 방문자 리뷰, 블로그 리뷰]
        if len(review) > 2:
            rating_xpath = f'.//div[2]/span[{_index}]'
            rating_element = title.find_element(By.XPATH, rating_xpath)
            rating = rating_element.text.replace("\n", " ")

            _index += 1

        try:
            # 방문자 리뷰
            visited_review = title.find_element(By.XPATH,f'.//div[2]/span[{_index}]/a').text


            # 인덱스를 다시 +1 증가 시킴
            _index += 1

            # 블로그 리뷰
            blog_review = title.find_element(By.XPATH,f'.//div[2]/span[{_index}]/a').text
        except:
            print(Colors.RED + '------------ 리뷰 부분 오류 ------------' + Colors.RESET)

        # 가게 id
        store_id = driver.find_element(By.XPATH,'//div[@class="flicking-camera"]/a').get_attribute('href').split('/')[4]







        # 가게 주소
        address = driver.find_element(By.XPATH,'//span[@class="LDgIH"]').text


        try:
            driver.find_element(By.XPATH,'//div[@class="y6tNq"]//span').click()

            # 영업 시간 더보기 버튼을 누르고 2초 반영시간 기다림
            sleep(2)


            parent_element = driver.find_element(By.XPATH,'//a[@class="gKP9i RMgN0"]')
            child_elements = parent_element.find_elements(By.XPATH, './*[@class="w9QyJ" or @class="w9QyJ undefined"]')

            for child in child_elements:
                # 각 자식 요소 내에서 클래스가 'A_cdD'인 span 요소 찾기
                span_elements = child.find_elements(By.XPATH, './/span[@class="A_cdD"]')

                # 찾은 span 요소들의 텍스트 출력
                for span in span_elements:
                    business_hours.append(span)
            
            # 가게 전화번호
            phone_num = driver.find_element(By.XPATH,'//span[@class="xlx7Q"]').text

        except:
            print(print(Colors.RED + '------------ 영업시간 / 전화번호 부분 오류 ------------' + Colors.RESET))
        
        print(Colors.BLUE + f'{index}. ' + str(store_name) + Colors.RESET + ' · ' + str(category) + Colors.RED + str(new_open) + Colors.RESET)
        print('평점 ' + Colors.RED + str(rating) + Colors.RESET + ' / ' + visited_review + ' · ' + blog_review)
        print(f'가게 고유 번호 -> {store_id}')
        print('가게 주소 ' + Colors.GREEN + str(address) + Colors.RESET)
        print(Colors.CYAN + '가게 영업 시간' + Colors.RESET)
        for i in business_hours:
            print(i.text)
            print('')
        print('가게 번호 ' + Colors.GREEN + phone_num + Colors.RESET)
        print(Colors.MAGENTA + "-"*50 + Colors.RESET)
    
    switch_left()
        
    # 페이지 다음 버튼이 활성화 상태일 경우 계속 진행
    if(next_page == 'false'):
        driver.find_element(By.XPATH,'//*[@id="app-root"]/div/div[3]/div[2]/a[7]').click()
    # 아닐 경우 루프 정지
    else:
        loop = False