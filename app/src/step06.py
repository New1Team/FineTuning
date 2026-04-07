from database.db import saveMany
from sessions.data import datalist

def save_data_first():
  """
  현재의 dataset을 DB에 저장하는 함수입니다. 초기 1회용
  """
  sql1 = None
  # 컬럼 수정시 sql2 value 수정하면 됨
  sql2 = f"""
        INSERT INTO `dataset` (`prompt`, `completion`) 
        VALUES(%s, %s)
        ON DUPLICATE KEY UPDATE
        prompt=VALUES(prompt),
        completion=VALUES(completion)
        """
  values = [(row["prompt"], row["completion"]) for row in datalist]
  saveMany(sql1, sql2, values)


def save_data(new_data_list):
  """
  추가된 프롬포트를 DB에 추가 저장하는 함수입니다.
  """
  data = new_data_list
  # 삭제 할 경우 sql1 수정
  # sql1 = f"DELETE FROM edu.`melon` WHERE `code` = '{code}'"
  sql1 = None
  # 컬럼 수정시 sql2 value 수정하면 됨
  sql2 = f"""
        INSERT INTO `dataset` (`prompt`, `completion`) 
        VALUES(%s, %s)
        ON DUPLICATE KEY UPDATE
        prompt=VALUES(prompt),
        completion=VALUES(completion)
        """
  values = [(row["prompt"], row["completion"]) for row in data]
  saveMany(sql1, sql2, values)
  return data

def run():
  """
  처음 DB에 데이터 추가시 프로그램 메인 로직 실행 함수
  """
  save_data_first()
if __name__ == "__main__":
  run()

# def run(new_data_list):
#   """
#   이후 new_data 추가시 프로그램 메인 로직 실행 함수
#   """
#   save_data(new_data_list)
  
# if __name__ == "__main__":
#   run()