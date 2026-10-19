# GitHub 트렌딩 주간 기록

매주 월요일 아침(한국 시간 6시 무렵) GitHub Actions가 [주간 트렌딩 페이지](https://github.com/trending?since=weekly)를 받아 저장합니다.

## 어디서 보나요?

- `weekly/` 폴더: 주차별 표 (GitHub에서 열면 바로 보기 좋게 표시됩니다)
- `data/latest.json`: 가장 최근 수집 결과 (프로그램이 읽는 용도)
- `data/날짜.json`: 주차별 원본 데이터

## 지금 바로 한 번 실행하려면

1. 저장소 위쪽의 **Actions** 탭을 엽니다.
2. 왼쪽에서 **Weekly GitHub Trending**을 누릅니다.
3. 오른쪽의 **Run workflow** 버튼을 누릅니다.
4. 1~2분 뒤 `weekly/` 폴더에 새 파일이 생깁니다.

## 실패했다면

GitHub가 트렌딩 페이지 구조를 바꾸면 수집이 실패하고 Actions 탭에 빨간 X가 뜹니다. 빈 기록은 남기지 않습니다. 이때는 `scripts/fetch_trending.py`의 파싱 부분을 고치면 됩니다.
