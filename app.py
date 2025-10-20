# 1. 必須インポート (Web操作に必要なものをすべて最初にインポート)
# import flask
from flask import Flask
# 環境変数を読み込むためのライブラリ
from dotenv import load_dotenv
# OSの環境変数にアクセスするための標準モジュール
import os
# import PyMySQL
import pymysql
import pymysql.cursors


# 2. 環境変数のロードと取得
# .env ファイル（ローカル設定）を読み込む
# Docker Composeで起動する場合、docker-compose.ymlで定義した環境変数が優先される
load_dotenv

# Docker Composeから渡されたMySQL接続情報を環境変数から取得し、変数に格納
# os.environ.get() を使用し、キーが見つからなかった場合のデフォルト値も設定する
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'your_default_password')
DB_NAME = os.environ.get('DB_NAME', 'test_db')

# 取得した情報を確認（任意：デバッグ用）
print("----- データベース接続情報 ----")
print(f"Host: {DB_HOST}")
print(f"User: {DB_USER}")
print(f"DB Name: {DB_NAME}")
print("-------------------------------")

# 3. Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)

# 4. クラスの定義 (CRUD関数がこのクラスに依存するため、先に定義)
# メモの情報を管理するクラス
class Memo:
  # コンストラクタを定義し、インスタンス生成時に属性を初期化
  def __init__(self, title, content, create_date):
    self.title = title                # メモのタイトル
    self.content = content            # メモの内容
    self.create_date = create_date    # メモ作成日
  
  # 後続のステップでデバッグに便利なメソッドを定義しておく
  def __repr__(self):
    return f"Memo(Title='{self.title}', Content='{self.content}')"

# 5. CRUD/データ操作関数
# データ挿入関数(insert)
# Memoオブジェクトを受け取り、MySQLのmemosテーブルに新しいレコードとして挿入する関数
def insert_memo(memo):
  conn = None
  try:
    # データベースへの接続確立
    conn = pymysql.connect(
      host=DB_HOST,
      user=DB_USER,
      password=DB_PASSWORD,
      database=DB_NAME,
      charset='utf8mb4',
      cursorclass=pymysql.cursors.DictCursor
    )
    # カーソル（SQLを実行するためのオブジェクト）を作成
    with conn.cursor() as cursor:
      # 挿入用のSQL文を定義
      # プレースホルダ (%s) を使用して、SQLインジェクション攻撃を防ぐ
      sql = """
      INSERT INTO memos (title, content, create_date)
      VALUES (%s, %s, %s, %s)
      """
      # Memoオブジェクトからデータを抽出してタプルに格納
      data = (
        memo.title,
        memo.content,
        memo.create_date
      )
      # SQLの実行（データは第2引数として渡す）
      cursor.execute(sql, data)
      # 6. 変更をコミット（確定）
      conn.commit()
      print(f"INFO: メモ '{memo.title}' をデータベースに挿入しました。")
  except Exception as e:
    print(f"ERROR: データ挿入中にエラーが発生しました: {e}")
    if conn:
      conn.rollback()
  finally:
    # 7. 接続を閉じる
    if conn:
      conn.close()

# データ取得の関数(Read)
# MySQLのmemosテーブルから全てのレコードを取得する関数
def get_all_memos():
  conn = None
  try:
    conn = pymysql.connect(
      host=DB_HOST,
      user=DB_USER,
      password=DB_PASSWORD,
      database=DB_NAME,
      charset='utf8mb4',
      cursorclass=pymysql.cursors.DictCursor
    )
    with conn.cursor() as cursor:
      # SQL: 全てのカラム(*)をmemosテーブルから選択
      sql = "SELECT id, title, content, create_date FROM memos"
      cursor.execute(sql)
      # 全ての結果をリスト形式で取得
      result = cursor.fetchall()
      return result
  except Exception as e:
    print(f"ERROR: 全データ取得中にエラーが発生しました: {e}")
    return []
  finally:
    if conn:
      conn.close()

# 特定の条件でレコードを取得する関数
def get_memo_by_id_or_title(identifier=None, title=None):
  conn = None
  try:
    conn = pymysql.connect(
      host=DB_HOST,
      user=DB_USER,
      password=DB_PASSWORD,
      database=DB_NAME,
      charset='utf8mb4',
      cursorclass=pymysql.cursors.DictCursor
    )
    with conn.cursor() as cursor:
      # SQL: 全てのカラム(*)をmemosテーブルから選択
      sql = "SELECT id, title, content, create_date FROM memos WHERE 1=1"
      params = []
      # IDが指定されたときの条件追加
      if identifier is not None:
        sql += " and ID = %s"
        params.append(identifier)
      # タイトルが指定されたときの条件追加（LIKEで部分一致検索も可能）
      if title is not None:
        sql += " AND title = %s"
        params.append(title)
      # SQLとパラメータを実行
      cursor.execute(sql, tuple(params))
      # 1件の結果のみ取得
      result = cursor.fetchall()
      return result
    
  except Exception as e:
    print(f"ERROR: 特定のデータ取得中にエラーが発生しました: {e}")
    return None
  finally:
    if conn:
      conn.close()

# レコードを更新する関数 (Update)
def update_memos():
  conn = None
  try:
    conn = pymysql.connect(
      host=DB_HOST,
      user=DB_USER,
      password=DB_PASSWORD,
      database=DB_NAME,
      charset='utf8mb4',
      cursorclass=pymysql.cursors.DictCursor
    )
    with conn.cursor() as cursor:
      # SQL: 全てのカラム(*)をmemosテーブルから選択
      sql = "UPDATE memos SET content = %s WHERE id %s"
      cursor.execute(sql, new_content)
    
      conn.commit()
      print(f"INFO: メモID {memo_id} の評価を {new_content} に更新しました。")
      return True
  except Exception as e:
    print(f"ERROR: データ更新中にエラーが発生しました: {e}")
    if conn:
      conn.rollback()
    return False
  finally:
    if conn:
      conn.close()




# 6. データベース初期化の実行
# MySQLデータベースに接続し、memosテーブルが存在しなければ作成する関数
def initialize_db():
  # 接続オブジェクトの初期化
  conn = None
  try:
    # データベースへの接続を確立し、環境変数を利用する
    conn = pymysql.connect(
      host=DB_HOST,
      user=DB_USER,
      password=DB_PASSWORD,
      database=DB_NAME,
      charset='utf8mb4',
      cursorclass=pymysql.cursors.DictCursor
    )
    # カーソル（SQLを実行するためのオブジェクト）を作成
    with conn.cursor() as cursor:
      # テーブル作成のSQLを定義
      # IF NOT EXISTS を付けることで、テーブルが既に存在する場合はエラーにならない
      sql = """
      CREATE TABLE IF NOT EXISTS books (
          id INT AUTO_INCREMENT PRIMARY KEY,
          title VARVHAR(255) NOT NULL,
          content VARCHAR(512) NOT NULL,
          create_date DATE
      )
      """
      # execute SQL
      cursor.execute(sql)
      # 変更をコミット
      conn,commit()
      print("INFO: memos")


# 7. Webルーティング
@app.route("/")
def index():
  return "<p>Hello, Flask</p>"

# 8. テストコード/実行ブロック