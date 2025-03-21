import subprocess
import sys

print("안녕하세요! 데이터 수집 크롤러, ⭐️와구별⭐️ 입니다!!")
while True:
    print("다운반고자 하는 데이터 번호를 입력해주세요.")
    print("-> 1. 질병 👿  2. 환경 🌱  3. 기후 🌞 (종료를 원하시면 0을 입력해주세요.)")
    
    type = int(input("번호 입력: ").strip())
    if type > 3:
        print("❌ 올바른 숫자를 입력해주세요!")
        continue

    if type == 0:
        print("감사합니다! 좋은하루 보내세요 ~ ❤️")
        sys.exit()
    elif type == 1:
        subprocess.run(["python", "find_dieases.py"])
    elif type == 2:
        subprocess.run(["python", "find_environment.py"])
    elif type == 3:
        subprocess.run(["python", "find_weather.py"])

