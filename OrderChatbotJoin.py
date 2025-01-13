import sqlite3
import os

# 데이터베이스 초기화 함수
def initialize_database():
    # Colab 환경에서는 데이터베이스 파일을 로컬 경로에 생성
    db_path = '/content/dialog_flow.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 기존 테이블 삭제
    cursor.execute("DROP TABLE IF EXISTS Dialog")
    cursor.execute("DROP TABLE IF EXISTS Transitions")

    # Dialog 테이블 생성
    cursor.execute('''
    CREATE TABLE Dialog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL
    )
    ''')

    # Transitions 테이블 생성
    cursor.execute('''
    CREATE TABLE Transitions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        current_id INTEGER NOT NULL,
        next_id INTEGER NOT NULL,
        FOREIGN KEY (current_id) REFERENCES Dialog(id),
        FOREIGN KEY (next_id) REFERENCES Dialog(id)
    )
    ''')

    # 초기 데이터 삽입
    cursor.executemany('''
    INSERT INTO Dialog (content)
    VALUES (?)
    ''', [
        ('안녕하세요! 무엇을 도와드릴까요?'),  # 1번 대화
        ('제품 정보를 알려드릴게요. 무엇을 찾으시나요?'),  # 2번 대화
        ('배송 상태를 확인하시겠어요? 주문 번호를 알려주세요.'),  # 3번 대화
        ('문의해주셔서 감사합니다. 다른 도움은 없으신가요?')  # 4번 대화
    ])

    cursor.executemany('''
    INSERT INTO Transitions (current_id, next_id)
    VALUES (?, ?)
    ''', [
        (1, 2),  # 대화 흐름: 1 -> 2
        (1, 3),  # 대화 흐름: 1 -> 3
        (2, 4),  # 대화 흐름: 2 -> 4
        (3, 4)   # 대화 흐름: 3 -> 4
    ])

    conn.commit()
    conn.close()

# 대화 흐름 관리 함수
def get_next_dialog(current_content):
    conn = sqlite3.connect('/content/dialog_flow.db')
    cursor = conn.cursor()

    # JOIN을 사용하여 현재 대화와 다음 대화 내용 가져오기
    query = '''
    SELECT NextDialog.content
    FROM Transitions
    JOIN Dialog AS CurrentDialog ON Transitions.current_id = CurrentDialog.id
    JOIN Dialog AS NextDialog ON Transitions.next_id = NextDialog.id
    WHERE CurrentDialog.content = ?
    '''
    cursor.execute(query, (current_content,))
    next_contents = cursor.fetchall()

    conn.close()

    if not next_contents:
        return None, "대화가 종료되었습니다."

    return [content[0] for content in next_contents], None

# 챗봇 실행 함수
def chatbot():
    initialize_database()

    print("안녕하세요! 대화 흐름 관리 챗봇입니다. '종료'를 입력하면 대화를 종료합니다.")

    current_content = '안녕하세요! 무엇을 도와드릴까요?'

    while True:
        print(f"챗봇: {current_content}")
        user_input = input("사용자: ").strip()

        if user_input.lower() == '종료':
            print("챗봇: 안녕히 가세요!")
            break

        next_contents, error = get_next_dialog(current_content)

        if error:
            print(f"챗봇: {error}")
            break

        # 간단한 흐름 시뮬레이션 (첫 번째 대화로 이동)
        if len(next_contents) == 1:
            current_content = next_contents[0]
        else:
            print("챗봇: 다음 선택지 중 하나를 선택하세요:")
            for idx, content in enumerate(next_contents, 1):
                print(f"{idx}. {content}")

            try:
                choice = int(input("선택: ")) - 1
                if 0 <= choice < len(next_contents):
                    current_content = next_contents[choice]
                else:
                    print("챗봇: 잘못된 선택입니다. 다시 시도해주세요.")
            except ValueError:
                print("챗봇: 숫자를 입력해주세요.")

# 실행
if __name__ == "__main__":
    chatbot()
