#!/bin/bash

# 사용법: ./run_large_v2.sh <fileName> [확장자]
# 예시: ./run_large_v2.sh audio mp3
# 예시: ./run_large_v2.sh audio (기본값: webm)

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "사용법: $0 <fileName> [확장자]"
    echo "예시: $0 audio mp3"
    echo "예시: $0 audio (기본값: webm)"
    exit 1
fi

fileName=$1
extension=${2:-webm}  # 두 번째 인자가 없으면 기본값으로 webm 사용

# resultFiles 디렉토리가 없으면 생성
mkdir -p resultFiles

# 현재 시간을 연월일시분초나노초 형식으로 생성
timestamp=$(date +"%Y%m%d%H%M%S%N" | cut -c1-17)  # 나노초는 6자리까지만 사용
output_file="resultFiles/${fileName}_${timestamp}.txt"

# 입력 파일 경로
input_file="targetFiles/${fileName}.${extension}"

# 입력 파일이 존재하는지 확인
if [ ! -f "$input_file" ]; then
    echo "오류: 입력 파일이 존재하지 않습니다: $input_file"
    exit 1
fi

echo "입력 파일: $input_file"
echo "출력 파일: $output_file"
echo "처리 중..."

# whisper-cli 실행
# 실시간으로 한 줄씩 처리하여 타임스탬프가 있는 라인만 파일에 즉시 저장
./whisper-cli -l ko -m models/ggml-large-v2.bin -f "$input_file" 2>&1 | while IFS= read -r line; do
    echo "$line"  # 터미널에 출력
    if echo "$line" | grep -q "^\[.*-->.*\]"; then
        echo "$line" >> "$output_file"  # 타임스탬프가 있는 라인만 파일에 즉시 추가
        # echo "${line}"  # 저장 확인 메시지
    fi
done

if [ $? -eq 0 ]; then
    echo "처리 완료! 음성 변환 텍스트가 저장되었습니다: $output_file"
else
    echo "처리 중 오류가 발생했습니다."
fi