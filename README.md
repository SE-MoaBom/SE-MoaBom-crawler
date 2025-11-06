# OTT Crawler Service

Playwright를 이용한 OTT 플랫폼 상영작 정보 크롤러

## 프로젝트 구조

```
SE-MoaBom-crawler/
├── src/                    # 소스 코드 디렉토리
│   ├── main.py            # 메인 실행 파일
│   ├── crawlers/          # 각 OTT별 크롤러
│   ├── database/          # DB 연결 및 저장 로직
│   └── utils/             # 유틸리티 함수
├── logs/                   # 로그 파일 디렉토리
├── Dockerfile             # Docker 이미지 정의
├── docker-compose.yml     # Docker Compose 설정
├── requirements.txt       # Python 의존성
├── crontab               # Cron 작업 정의
├── start.sh              # 컨테이너 시작 스크립트
├── .env                  # 환경 변수 (생성 필요)
└── .env.example          # 환경 변수 예시

```

## 설치 및 실행

### 1. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 열어 실제 값으로 수정
```

### 2. Docker Compose로 실행

```bash
# 빌드 및 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

## Cron 스케줄

- **실행 시간**: 매일 새벽 5시 (한국 시간 기준)
- **작업**: OTT 플랫폼 상영작 정보 크롤링 및 DB 저장

## 로그

- 크롤러 로그: `./logs/app.log`
- Cron 실행 로그: `./logs/cron.log`

## 개발 환경

- Python 3.13
- Playwright (Chromium)
- Docker & Docker Compose
- Cron
