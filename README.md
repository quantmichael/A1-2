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