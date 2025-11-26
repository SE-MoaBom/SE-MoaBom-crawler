#!/bin/bash

# 환경 변수 출력 (디버깅용)
echo "Starting OTT Crawler Service..."
echo "Timezone: $TZ"
echo "Current time: $(date)"

# Cron 서비스 시작
service cron start

# 컨테이너 시작 시 1회 즉시 실행 (테스트용)
echo "Running crawler immediately..."
/usr/local/bin/python /app/src/main.py

# Cron 로그를 실시간으로 출력 (컨테이너가 종료되지 않도록)
tail -f /var/log/cron.log
