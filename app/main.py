from src import step06, datalist

def main():
  print("작업을 시작합니다.")
  new_data = [
        {"prompt": "질문 프롬포트 A", "completion": "답변 A"},
        {"prompt": "질문 프롬포트 B", "completion": "답변 B"}
    ]
  # new_data를 추가하는 경우 실행
  # datalist.run(new_data) # data.py에 추가
  # step06.run(new_data) # DB에 추가
  # print(f"DB에 {new_data}가 추가가 완료되었습니다.")

  # 전체 data를 추가하는 경우 실행
  step06.run()
  print("DB에 데이터를 저장하였습니다.")
if __name__ == "__main__":
  main()
