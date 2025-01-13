import sqlite3
from konlpy.tag import Okt
import os

# KoNLPy 형태소 분석기 초기화
okt = Okt()

# 데이터베이스 초기화 함수
def initialize_database():

    # Colab 환경에서는 데이터베이스 파일을 로컬 경로에 생성
    db_path = '/content/recipe_chatbot.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 기존 테이블 삭제
    cursor.execute("DROP TABLE IF EXISTS Recipes")

    # Recipes 테이블 생성
    cursor.execute('''
    CREATE TABLE Recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        ingredients TEXT NOT NULL,
        instructions TEXT NOT NULL
    )
    ''')

    # 초기 데이터 삽입
    cursor.executemany('''
    INSERT INTO Recipes (name, ingredients, instructions)
    VALUES (?, ?, ?)
    ''', [
        ('김치찌개', '김치, 돼지고기, 두부, 대파, 고춧가루', '1. 김치를 볶는다. 2. 돼지고기를 추가하여 볶는다. 3. 물을 넣고 끓인다. 4. 두부와 대파를 넣는다.'),
        ('된장찌개', '된장, 두부, 애호박, 감자, 양파', '1. 된장을 풀어 물에 끓인다. 2. 애호박, 감자, 양파를 넣는다. 3. 두부를 추가하고 한소끔 끓인다.'),
        ('불고기', '소고기, 간장, 설탕, 마늘, 대파', '1. 소고기를 양념에 재운다. 2. 팬에 재운 고기를 구워낸다.'),
        ('비빔밥', '밥, 나물, 고추장, 달걀', '1. 밥 위에 나물을 얹는다. 2. 고추장과 달갈을 올린 후 비빈다.')
    ])

    conn.commit()
    conn.close()

# 사용자 입력에서 주요 키워드 추출
def extract_keywords(user_input):
    return okt.nouns(user_input)  # 입력 문장에서 명사만 추출

# 사용자 입력을 기반으로 레시피 검색
def find_recipes(user_input):
    keywords = extract_keywords(user_input)
    conn = sqlite3.connect('/content/recipe_chatbot.db')
    cursor = conn.cursor()

    # 검색 결과 담기
    results = []
    for keyword in keywords:
        # 레시피 이름에서도 검색하도록 확장
        cursor.execute("SELECT name, ingredients, instructions FROM Recipes WHERE name LIKE ? OR ingredients LIKE ?", (f'%{keyword}%', f'%{keyword}%'))
        results.extend(cursor.fetchall())

    conn.close()
    return results

# 챗봇 실행 함수
def chatbot():
    initialize_database()

    print("안녕하세요! 음식 레시피 추천 챗봇입니다. '종료'를 입력하면 대화를 종료합니다.")

    while True:
        user_input = input("사용자: ").strip()
        if user_input.lower() == '종료':
            print("챗봇: 안녕히 가세요!")
            break

        # 레시피 검색
        recipes = find_recipes(user_input)

        if recipes:
            print("챗봇: 다음 레시피를 추천합니다:")
            for recipe in recipes:
                name, ingredients, instructions = recipe
                print(f"\n[레시피: {name}]\n재료: {ingredients}\n조리법: {instructions}")
        else:
            print("챗봇: 해당 재료나 이름으로 만들 수 있는 레시피를 찾지 못했습니다. 다른 재료로 시도해 보세요.")

# 실행
if __name__ == "__main__":
    chatbot()
