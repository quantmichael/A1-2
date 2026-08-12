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

def get_travel_recommendation(api_key, travel_date):
    url = "https://api.openai.com/v1/responses"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

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
    """

    data = {
        "model": "gpt-5-mini",
        "input": prompt
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=30
    )

    return response

def search_kakao_places(api_key, query):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"

    headers = {
        "Authorization": f"KakaoAK {api_key}"
    }

    params = {
        "query": query,
        "size": 5
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30
    )

    return response

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

    args = parser.parse_args()

    if not validate_date(args.date):
        parser.error(
            "날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력하세요."
        )

    print("입력한 여행 날짜:", args.date)
    print("OpenAI API Key:", "설정됨" if openai_api_key else "없음")
    print("Kakao API Key:", "설정됨" if kakao_api_key else "없음")

    if openai_api_key:
        response = get_travel_recommendation(
            openai_api_key,
            args.date
        )

        response_data = response.json()
        text = response_data["output"][1]["content"][0]["text"]

        recommendation = json.loads(text)

        city = recommendation["recommended_city"]

        print("추천 지역:", city)
        print("날씨:", recommendation["weather"])
        print("행사:", recommendation["events"])
        print("추천 이유:", recommendation["reason"])

        if kakao_api_key:
            query = f"{city} 맛집"

            kakao_response = search_kakao_places(
                kakao_api_key,
                query
            )

            print("Kakao API 상태 코드:", kakao_response.status_code)
            print("검색어:", query)

            restaurants = extract_restaurants(kakao_response)

            print(f"맛집 검색 결과: {len(restaurants)}곳")

            for index, restaurant in enumerate(restaurants, start=1):
                print(f"\n{index}. {restaurant['name']}")
                print(f"   주소: {restaurant['address']}")
                print(f"   카테고리: {restaurant['category']}")
                print(f"   URL: {restaurant['url']}")

        else:
            print("Kakao API Key가 설정되지 않았습니다.")

if __name__ == "__main__":
    main()