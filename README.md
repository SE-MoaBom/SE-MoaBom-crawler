# OTT Crawler Service

Playwright 기반의 비동기 Python 크롤러로, 키노라이츠(Kinolights)에서 OTT 플랫폼(공개 예정, 종료 예정, 랭킹 등) 상영작 정보를 수집하여 MySQL 데이터베이스에 저장합니다. 크롤러는 Docker 컨테이너 환경에서 주기적으로 실행되며, 수집된 데이터는 프로그램, OTT, 이용 가능 정보 등으로 정규화되어 저장됩니다.

## 프로젝트 구조

```
SE-MoaBom-crawler/
├── src/
│   ├── main.py           # 크롤러 실행 메인 엔트리포인트
│   ├── crawlers/         # 크롤러 계층 (upcoming, expired, ranking 등)
│   ├── db/               # DB 연결, ORM 모델, 레포지토리
│   ├── models/           # 데이터 모델(Pydantic, dataclass, Enum)
│   └── utils/            # 설정, 로깅 등 유틸리티
├── compose.yaml          # 크롤러 서비스용 Docker Compose
├── sql_compose.yaml      # DB 서비스용 Docker Compose
├── crontab               # Cron 작업 정의
├── start.sh              # 컨테이너 시작 스크립트
```

## 설치 및 실행

### 1. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 열어 실제 값으로 수정
```

### 2. 의존성 설치 (로컬 개발 시)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Docker Compose로 실행

```bash
# 빌드 및 실행
docker compose up -d --build

# 로그 확인
docker compose logs -f

# 중지
docker compose down
```

## Cron
