import argparse
import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv


def validate_date(date_string):
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def get_travel_recommendation(api_key, travel_date, retry=False):
    url = "https://api.openai.com/v1/responses"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    retry_instruction = ""

    if retry:
        retry_instruction = """
    이전 응답은 JSON 파싱에 실패했습니다.

    이번에는 반드시 아래 조건을 지켜주세요.

    - JSON 객체 하나만 출력
    - ```json 같은 코드 블록 사용 금지
    - JSON 앞뒤에 설명문 작성 금지
    - 모든 key와 문자열은 큰따옴표 사용
    - 마지막 쉼표 사용 금지
    """
        
    prompt = f"""
    여행 날짜는 {travel_date}입니다.

    이 날짜에 여행하기 좋은 대한민국 국내 여행지 1곳을 추천해주세요.

    반드시 아래 JSON 형식으로만 답변해주세요.

    {{
        "recommended_city": "도시명만 작성. 예: 부산, 제주, 강릉, 경주",
        "weather": "예상 날씨 요약",
        "events": ["행사 또는 축제 정보"],
        "reason": "추천 이유"
    }}

    recommended_city에는 검색에 바로 사용할 수 있는 지역명 하나만 작성하세요.
    괄호, 관광지명, 부가 설명은 포함하지 마세요.

    좋은 예:
    "recommended_city": "부산"

    잘못된 예:
    "recommended_city": "부산 (해운대·광안리)"

    JSON 이외의 설명은 작성하지 마세요.

    {retry_instruction}
    """

    data = {
        "model": "gpt-5-mini",
        "input": prompt
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=60
        )

        return response

    except requests.exceptions.Timeout:
        print("오류: OpenAI API 응답 시간이 초과되었습니다.")
        return None

    except requests.exceptions.RequestException as error:
        print(f"오류: OpenAI API 호출에 실패했습니다. ({error})")
        return None

def search_places(api_key, query):
    """
    장소 검색 공통 인터페이스.

    입력:
        api_key: 장소 검색 API 인증 키
        query: 검색할 지역/키워드 문자열

    출력:
        requests.Response 객체 또는 None

    현재 구현은 Kakao Local API를 사용한다.
    다른 장소 검색 API로 교체할 경우 이 함수 내부의 호출 대상을 변경한다.
    """
    return search_kakao_places(api_key, query)

def search_kakao_places(api_key, query):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"

    headers = {
        "Authorization": f"KakaoAK {api_key}"
    }

    params = {
        "query": query,
        "size": 5
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30
        )

        return response

    except requests.exceptions.Timeout:
        print("오류: Kakao API 응답 시간이 초과되었습니다.")
        return None

    except requests.exceptions.RequestException as error:
        print(f"오류: Kakao API 호출에 실패했습니다. ({error})")
        return None

def extract_restaurants(kakao_response):
    data = kakao_response.json()
    documents = data.get("documents", [])

    restaurants = []

    for place in documents:
        restaurant = {
            "name": place.get("place_name", ""),
            "address": place.get("road_address_name") or place.get("address_name", ""),
            "category": place.get("category_name", ""),
            "url": place.get("place_url", ""),
            "x": place.get("x", ""),
            "y": place.get("y", "")
        }

        restaurants.append(restaurant)

    return restaurants

def create_final_report(
    api_key,
    travel_date,
    recommendation,
    restaurants,
    errors
):
    url = "https://api.openai.com/v1/responses"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    restaurants_text = json.dumps(
        restaurants,
        ensure_ascii=False,
        indent=2
    )

    errors_text = json.dumps(
        errors,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
여행 날짜: {travel_date}

다음은 1차 여행 추천 정보입니다.

추천 지역: {recommendation["recommended_city"]}
날씨: {recommendation["weather"]}
행사/축제: {recommendation["events"]}
추천 이유: {recommendation["reason"]}

다음은 Kakao Local API에서 검색한 맛집 정보입니다.

{restaurants_text}

다음은 실행 중 수집된 오류 정보입니다.

{errors_text}

위 정보를 바탕으로 국내 1일 여행 리포트를 작성해주세요.

반드시 다음 내용을 포함해주세요.

1. 추천 지역
2. 추천 이유
3. 날씨 요약
4. 행사 또는 축제
5. 맛집 추천
6. 오전, 점심, 오후, 저녁으로 구성된 1일 일정
7. 오류 정보가 있다면 마지막에 "오류 및 주의사항" 항목으로 요약

Markdown 형식으로 작성해주세요.
"""

    data = {
        "model": "gpt-5-mini",
        "input": prompt
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=60
        )

        return response

    except requests.exceptions.Timeout:
        print("오류: OpenAI API 응답 시간이 초과되었습니다.")
        return None

    except requests.exceptions.RequestException as error:
        print(f"오류: OpenAI API 호출에 실패했습니다. ({error})")
        return None

def save_json_result(travel_date, recommendation, restaurants, errors):
    os.makedirs("results", exist_ok=True)

    result_data = {
        "date": travel_date,
        "recommendation": recommendation,
        "restaurants": restaurants,
        "errors": errors
    }

    file_path = f"results/{travel_date}_travel_data.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            result_data,
            file,
            ensure_ascii=False,
            indent=2
        )

    return file_path

def load_json_result(travel_date):
    """저장된 여행 데이터를 불러온다. 캐시가 없거나 손상되면 None을 반환한다."""
    file_path = f"results/{travel_date}_travel_data.json"

    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            result_data = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        print(f"캐시 파일을 읽지 못했습니다: {error}")
        return None

    required_keys = {
        "date",
        "recommendation",
        "restaurants",
        "errors"
    }

    if not required_keys.issubset(result_data):
        print("캐시 파일에 필수 데이터가 없습니다. API를 다시 호출합니다.")
        return None

    return result_data

def save_markdown_report(travel_date, final_report):
    os.makedirs("results", exist_ok=True)

    file_path = f"results/{travel_date}_travel_plan.md"

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(final_report)

    return file_path

def check_api_response(response, api_name):
    if response.status_code == 200:
        return True

    if response.status_code == 401:
        print(f"오류: {api_name} API 인증에 실패했습니다. API 키를 확인해주세요.")

    elif response.status_code == 403:
        print(f"오류: {api_name} API 사용 권한이 없습니다.")

    elif response.status_code == 429:
        print(f"오류: {api_name} API 호출 한도 또는 사용량을 초과했습니다.")

    elif 500 <= response.status_code < 600:
        print(f"오류: {api_name} 서버에 문제가 발생했습니다.")

    else:
        print(
            f"오류: {api_name} API 호출에 실패했습니다. "
            f"(상태 코드: {response.status_code})"
        )

    return False

def parse_recommendation_response(response):
    text = extract_openai_text(response)

    if text is None:
        return None

    try:
        recommendation = json.loads(text)

    except json.JSONDecodeError:
        print("오류: OpenAI 추천 결과를 JSON으로 변환하지 못했습니다.")
        return None

    required_keys = [
        "recommended_city",
        "weather",
        "events",
        "reason"
    ]

    for key in required_keys:
        if key not in recommendation:
            print(f"오류: 추천 결과에 '{key}' 항목이 없습니다.")
            return None

    if not isinstance(recommendation["recommended_city"], str):
        print("오류: recommended_city는 문자열이어야 합니다.")
        return None

    if not isinstance(recommendation["weather"], str):
        print("오류: weather는 문자열이어야 합니다.")
        return None

    if not isinstance(recommendation["events"], list):
        print("오류: events는 리스트여야 합니다.")
        return None

    if not isinstance(recommendation["reason"], str):
        print("오류: reason은 문자열이어야 합니다.")
        return None

    return recommendation

def extract_openai_text(response):
    try:
        response_data = response.json()
        return response_data["output"][1]["content"][0]["text"]

    except (KeyError, IndexError, TypeError):
        print("오류: OpenAI 응답에서 텍스트를 찾지 못했습니다.")
        return None

def normalize_city_name(city):
    city = city.strip()

    if "(" in city:
        city = city.split("(")[0].strip()

    return city
      
def main():
    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    kakao_api_key = os.getenv("KAKAO_REST_API_KEY")

    parser = argparse.ArgumentParser(
        description="국내 여행지 추천 프로그램"
    )

    parser.add_argument(
        "--date",
        required=True,
        help="여행 날짜를 YYYY-MM-DD 형식으로 입력하세요."
    )

    parser.add_argument(
        "--refresh",
        action="store_true",
        help="저장된 JSON 캐시를 무시하고 API를 다시 호출합니다."
    )

    args = parser.parse_args()

    if not validate_date(args.date):
        parser.error(
            "날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력하세요."
        )

    errors = []

    if not openai_api_key:
        print("오류: OPENAI_API_KEY가 설정되지 않았습니다.")
        print(".env 파일에 OPENAI_API_KEY를 설정해주세요.")
        return

    cached_data = None

    if not args.refresh:
        cached_data = load_json_result(args.date)

    if cached_data is not None:
        print(f"저장된 JSON 캐시를 불러왔습니다: results/{args.date}_travel_data.json")

        final_response = create_final_report(
            openai_api_key,
            cached_data["date"],
            cached_data["recommendation"],
            cached_data["restaurants"],
            cached_data["errors"]
        )

        if final_response is None:
            print("캐시 데이터로 최종 여행 리포트를 생성하지 못했습니다.")
            return

        if not check_api_response(final_response, "OpenAI"):
            return

        final_report = extract_openai_text(final_response)

        if final_report is None:
            print("최종 여행 리포트 내용을 가져오지 못했습니다.")
            return

        print("\n========== 캐시 기반 최종 여행 리포트 ==========\n")
        print(final_report)

        markdown_file = save_markdown_report(args.date, final_report)
        print("\nJSON 캐시를 사용해 리포트를 다시 생성했습니다.")
        print("Markdown:", markdown_file)
        return

    if not kakao_api_key:
        print("오류: KAKAO_REST_API_KEY가 설정되지 않았습니다.")
        print(".env 파일에 KAKAO_REST_API_KEY를 설정해주세요.")
        return
    
    print("입력한 여행 날짜:", args.date)
    print("OpenAI API Key:", "설정됨" if openai_api_key else "없음")
    print("Kakao API Key:", "설정됨" if kakao_api_key else "없음")

    response = get_travel_recommendation(
        openai_api_key,
        args.date
    )

    if response is None:
        print("여행 추천 정보를 가져오지 못했습니다.")
        return

    if not check_api_response(response, "OpenAI"):
        return

    recommendation = parse_recommendation_response(response)

    if recommendation is None:
        print("추천 JSON 파싱에 실패했습니다. 1회 재시도합니다.")

        retry_response = get_travel_recommendation(
            openai_api_key,
            args.date,
            retry=True
        )

        if retry_response is None:
            print("재시도 중 OpenAI 응답을 받지 못했습니다.")
            return

        if not check_api_response(retry_response, "OpenAI"):
            return

        recommendation = parse_recommendation_response(retry_response)

        if recommendation is None:
            print("재시도 후에도 추천 JSON 파싱에 실패했습니다.")
            return

    city = normalize_city_name(
        recommendation["recommended_city"]
    )
    
    print("추천 지역:", city)
    print("날씨:", recommendation["weather"])
    print("행사:", recommendation["events"])
    print("추천 이유:", recommendation["reason"])

    query = f"{city} 맛집"

    kakao_response = search_places(
        kakao_api_key,
        query
    )

    if kakao_response is None:
        error_message = "맛집 검색 정보를 가져오지 못했습니다."
        print(error_message)
        errors.append(error_message)
        restaurants = []
    elif not check_api_response(kakao_response, "Kakao"):
        restaurants = []
    else:
        print("Kakao API 상태 코드:", kakao_response.status_code)
        restaurants = extract_restaurants(kakao_response)

    print("검색어:", query)

    if len(restaurants) == 0:
        error_message = "맛집 검색 결과가 없습니다."
        print(error_message)
        errors.append(error_message)
    else:
        print(f"맛집 검색 결과: {len(restaurants)}곳")

        for index, restaurant in enumerate(restaurants, start=1):
            print(f"\n{index}. {restaurant['name']}")
            print(f"   주소: {restaurant['address']}")
            print(f"   카테고리: {restaurant['category']}")
            print(f"   URL: {restaurant['url']}")



    final_response = create_final_report(
        openai_api_key,
        args.date,
        recommendation,
        restaurants,
        errors
    )

    if final_response is None:
        print("최종 여행 리포트를 생성하지 못했습니다.")
        return

    if not check_api_response(final_response, "OpenAI"):
        return
    
    print("\n최종 리포트 API 상태 코드:", final_response.status_code)

    final_report = extract_openai_text(final_response)

    if final_report is None:
        print("최종 여행 리포트 내용을 가져오지 못했습니다.")
        return

    print("\n========== 최종 여행 리포트 ==========\n")
    print(final_report)

    json_file = save_json_result(
        args.date,
        recommendation,
        restaurants,
        errors
    )

    markdown_file = save_markdown_report(
        args.date,
        final_report
    )

    print("\n파일 저장 완료")
    print("JSON:", json_file)
    print("Markdown:", markdown_file)    


if __name__ == "__main__":
    main()
