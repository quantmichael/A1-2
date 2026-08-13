# 국내 여행지 추천 프로그램

## 1. 프로그램 개요

사용자가 여행 날짜를 입력하면 OpenAI API를 이용해 해당 날짜에 추천할 국내 여행지를 생성하고, Kakao Local API를 이용해 추천 지역의 맛집을 검색합니다.

이후 추천 정보와 맛집 정보를 다시 OpenAI API에 전달하여 최종 1일 여행 리포트를 생성합니다.

프로그램 실행 결과는 JSON 파일과 Markdown 파일로 저장됩니다.

## 2. 주요 기능

- CLI 기반 여행 날짜 입력
- YYYY-MM-DD 형식의 날짜 검증
- OpenAI API를 이용한 국내 여행지 추천
- 추천 결과 JSON 파싱
- 추천 지역을 이용한 Kakao Local 맛집 검색
- 맛집 정보 추출
- 추천 정보와 맛집 정보를 활용한 최종 여행 리포트 생성
- JSON 원본 데이터 저장
- Markdown 여행 리포트 저장
- API 오류 및 네트워크 오류 처리

## 3. 개발 환경

- Python 3.10 이상
- requests
- python-dotenv

필요한 라이브러리는 다음 명령으로 설치할 수 있습니다.

```bash
python -m pip install requests python-dotenv
```

## 4. API 키 설정

프로젝트 폴더에 `.env` 파일을 생성합니다.

`.env` 파일에 다음과 같이 OpenAI API 키와 Kakao REST API 키를 입력합니다.

```text
OPENAI_API_KEY=본인의_OpenAI_API_Key
KAKAO_REST_API_KEY=본인의_Kakao_REST_API_Key
```

API 키는 외부에 공개되지 않도록 주의해야 합니다.

`.gitignore` 파일에는 다음 내용을 포함합니다.

```text
.env
__pycache__/
```

## 5. 실행 방법

터미널에서 다음 형식으로 실행합니다.

```bash
python travel_planner.py --date "2026-08-15"
```

날짜는 반드시 `YYYY-MM-DD` 형식으로 입력해야 합니다.

예:

```bash
python travel_planner.py --date "2026-12-25"
```

## 6. 프로그램 실행 흐름

```text
여행 날짜 입력
        ↓
OpenAI API
        ↓
추천 지역 / 날씨 / 행사 / 추천 이유
        ↓
추천 지역 추출
        ↓
Kakao Local API
        ↓
맛집 검색
        ↓
OpenAI API
        ↓
최종 1일 여행 리포트
        ↓
JSON / Markdown 저장
```

## 7. 결과 파일

프로그램 실행이 정상적으로 완료되면 `results` 폴더에 결과가 저장됩니다.

예:

```text
results/
├── 2026-08-15_travel_data.json
└── 2026-08-15_travel_plan.md
```

### JSON 파일

JSON 파일에는 다음 정보가 저장됩니다.

- 여행 날짜
- 추천 지역
- 날씨
- 행사 또는 축제
- 추천 이유
- 맛집 검색 결과
- 오류 정보

### Markdown 파일

Markdown 파일에는 최종 여행 리포트가 저장됩니다.

최종 리포트에는 다음 내용이 포함됩니다.

- 추천 지역
- 추천 이유
- 날씨 요약
- 행사 또는 축제
- 맛집 추천
- 오전, 점심, 오후, 저녁으로 구성된 1일 일정

## 8. 오류 처리

프로그램은 다음 상황에 대해 오류 처리를 수행합니다.

- 잘못된 날짜 형식
- API 키 누락
- OpenAI API 인증 오류
- Kakao API 인증 및 권한 오류
- API 호출 한도 초과
- API 서버 오류
- 네트워크 오류 및 Timeout
- OpenAI JSON 파싱 오류
- 필수 추천 데이터 누락
- Kakao 맛집 검색 결과 없음

## 9. API 키 보안 주의사항

API 키는 Python 코드에 직접 작성하지 않고 `.env` 파일을 이용해 관리합니다.

`.env` 파일은 Git 저장소에 업로드하지 않아야 하므로 `.gitignore`에 반드시 등록합니다.

공용 PC에서 프로그램을 실행한 경우 작업이 끝난 뒤 `.env` 파일에 저장된 실제 API 키를 제거하는 것이 안전합니다.

## 10. 장소 검색 API 교체

현재 장소 검색은 Kakao Local API를 사용합니다.

프로그램에서는 `search_places(api_key, query)`를 장소 검색의 공통 인터페이스로 사용하며, 현재 이 함수 내부에서 `search_kakao_places()`를 호출합니다.

다른 장소 검색 제공자로 교체할 경우 `search_places()` 내부의 호출 함수를 변경하고, 반환되는 장소 데이터를 `name`, `address`, `category`, `url`, `x`, `y` 형식에 맞게 변환하면 됩니다.

추천 도시명은 장소 검색 전에 앞뒤 공백과 괄호 뒤의 부가 설명을 제거하여 검색어를 정규화합니다.

## 11. API 엔드포인트 및 HTTP 메서드

### OpenAI API

- 엔드포인트: `https://api.openai.com/v1/responses`
- HTTP 메서드: `POST`
- 용도: 여행지 추천 및 최종 여행 리포트 생성

OpenAI Responses API는 모델에 프롬프트와 모델 정보 등의 데이터를 전달하여 새로운 응답을 생성해야 하므로 POST 방식으로 요청합니다.

요청 데이터에는 모델명과 사용자 입력 프롬프트가 JSON 형식으로 포함됩니다.

### Kakao Local API

- 엔드포인트: `https://dapi.kakao.com/v2/local/search/keyword.json`
- HTTP 메서드: `GET`
- 용도: 추천 지역의 맛집 검색

Kakao Local 키워드 검색 API는 서버에 새로운 데이터를 생성하는 것이 아니라 검색 조건에 해당하는 장소 정보를 조회하는 API이므로 GET 방식으로 요청합니다.

검색어는 `query` 파라미터로 전달하며, 프로그램에서는 OpenAI가 추천한 지역명을 이용하여 다음과 같은 검색어를 생성합니다.

`추천지역 + " 맛집"`

예:

`부산 맛집`

## 12. LLM 응답을 JSON 형식으로 사용하는 이유

OpenAI의 여행지 추천 결과는 자유로운 문장이 아니라 JSON 형식으로 받도록 프롬프트를 구성했습니다.

JSON 형식을 사용하면 `recommended_city`, `weather`, `events`, `reason`과 같은 값을 프로그램에서 명확하게 구분하여 파싱할 수 있습니다.

특히 `recommended_city` 값을 추출하여 Kakao Local API의 검색어로 바로 사용할 수 있기 때문에, LLM의 출력을 다음 API 호출의 입력으로 안정적으로 연결할 수 있습니다.

또한 필수 키의 존재 여부와 데이터 타입을 검사할 수 있어 자유 형식의 텍스트 응답보다 오류를 발견하고 처리하기 쉽습니다.

LLM 추천 결과가 JSON으로 파싱되지 않거나 필수 데이터 형식이 올바르지 않으면 최대 1회 재시도합니다. 재시도 시에는 JSON 객체만 출력하도록 프롬프트를 강화하며, 재시도 후에도 파싱 또는 검증에 실패하면 프로그램을 종료합니다.

## 13. API 인증 및 권한 오류 확인 방법

API 호출 중 `401` 또는 `403` 오류가 발생하면 다음 항목을 확인합니다.

### OpenAI API

- `.env` 파일의 `OPENAI_API_KEY` 값이 올바른지 확인
- API 키 앞뒤에 공백이나 잘못된 문자가 포함되지 않았는지 확인
- `Authorization: Bearer API_KEY` 형식으로 헤더가 전달되는지 확인
- API 키가 만료되었거나 비활성화되지 않았는지 확인
- OpenAI API 사용량 또는 결제 상태를 확인

### Kakao Local API

- `.env` 파일의 `KAKAO_REST_API_KEY` 값이 올바른 REST API 키인지 확인
- JavaScript 키가 아닌 REST API 키를 사용하고 있는지 확인
- `Authorization: KakaoAK REST_API_KEY` 형식으로 헤더가 전달되는지 확인
- Kakao Developers에서 해당 애플리케이션의 카카오맵/Local API 사용 설정이 활성화되어 있는지 확인
- 앱 설정 및 API 사용 권한을 확인

### 공통 확인 사항

- 상태 코드와 응답 메시지를 콘솔에서 확인
- API 키를 로그나 README에 직접 출력하지 않도록 주의
- 네트워크 연결 상태를 확인
- 문제가 지속되면 API 제공자의 개발자 콘솔 또는 공식 문서에서 인증 상태를 확인

## 14. 결과 재사용 및 캐싱 정책

프로그램 실행 결과는 날짜별로 `results/` 디렉터리에 JSON과 Markdown 파일로 저장됩니다.

현재 프로그램은 같은 날짜의 결과 파일이 이미 존재하더라도 자동으로 재사용하지 않고 API를 다시 호출합니다. 여행지 추천, 장소 검색 등의 정보가 변경될 수 있으므로 실행 시점의 결과를 다시 생성하는 방식을 사용합니다.

따라서 같은 날짜로 다시 실행하면 기존 결과 파일은 새로운 실행 결과로 갱신됩니다.

향후 API 호출 비용이나 실행 시간을 줄여야 하는 경우에는 날짜별 JSON 파일의 존재 여부를 확인하여 기존 결과를 재사용하는 캐싱 기능을 추가할 수 있습니다.
