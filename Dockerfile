# Python 3.13 slim 이미지 사용
FROM python:3.13-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    cron \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# Playwright 브라우저 설치
RUN playwright install chromium
RUN playwright install-deps chromium

# 애플리케이션 코드 복사
COPY . .

# 로그 디렉토리 생성
RUN mkdir -p /var/log/crawler

# Cron 작업 설정 파일 복사
COPY crontab /etc/cron.d/crawler-cron

# Cron 파일 권한 설정
RUN chmod 0644 /etc/cron.d/crawler-cron

# Cron 작업 등록
RUN crontab /etc/cron.d/crawler-cron

# Cron 로그 파일 생성
RUN touch /var/log/cron.log

# 시작 스크립트 실행 권한 부여
RUN chmod +x /app/start.sh

# 컨테이너 시작 시 실행할 명령
CMD ["/app/start.sh"]
