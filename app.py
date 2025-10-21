# 1. 必須インポート (Web操作に必要なものをすべて最初にインポート)
# import flask
from flask import Flask, render_template, request, redirect, url_for
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
      VALUES (%s, %s, %s)
      """
      # Memoオブジェクトからデータを抽出してタプルに格納
      data = (
        memo.title,
        memo.content,
        memo.create_date
      )
      # SQLの実行（データは第2引数として渡す）
      cursor.execute(sql, (memo.title, memo.content, memo.create_date))
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
def update_memo(memo_id, new_title, new_content):
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
      sql = "UPDATE memos SET title = %s, content = %s WHERE id = %s"
      cursor.execute(sql, (new_title, new_content, memo_id))
    
      conn.commit()
      print(f"INFO: メモID {memo_id} の内容を {new_title} と {new_content} に更新しました。")
      return True
  except Exception as e:
    print(f"ERROR: データ更新中にエラーが発生しました: {e}")
    if conn:
      conn.rollback()
    return False
  finally:
    if conn:
      conn.close()

# レコードを削除する関数 (Delete)
# 特定のIDの書籍レコードをデータベースから削除する関数
def delete_memo(memo_id):
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
            # SQL: booksテーブルから、IDが一致するレコードを削除
            sql = "DELETE FROM memos WHERE id = %s"
            # パラメータのタプルを定義 (book_id,) *タプルにするためにカンマが必要
            cursor.execute(sql, (memo_id,)) 
            
            if cursor.rowcount == 0:
                print(f"WARN: ID {memo_id} のメモが見つからなかったため、削除されませんでした。")
                return False

            conn.commit()
            print(f"INFO: メモID {memo_id} をデータベースから削除しました。")
            return True

    except Exception as e:
        print(f"ERROR: データ削除中にエラーが発生しました: {e}")
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
      CREATE TABLE IF NOT EXISTS memos (
          id INT AUTO_INCREMENT PRIMARY KEY,
          title VARCHAR(255) NOT NULL,
          content VARCHAR(512) NOT NULL,
          create_date DATE
      )
      """
      # execute SQL
      cursor.execute(sql)
      # 変更をコミット
      conn.commit()
      print("INFO: memos テーブルの初期化が完了しました")
  except Exception as e:
        print(f"ERROR: データベース接続またはテーブル作成中にエラーが発生しました: {e}")
        # エラー発生時はロールバック（取り消し）
        if conn:
            conn.rollback()
  finally:
    # 6. 接続を閉じる
    if conn:
        conn.close()
# Flaskアプリケーションの起動前にデータベース初期化を実行
# アプリケーション全体でこの処理を一度実行したい場所に記述
initialize_db()


# 7. Webルーティング
@app.route("/")
def index():
  # return "<p>Hello, Flask</p>"
  # データベースから全書籍データを取得
  memos_data = get_all_memos()
  # 取得したデータを 'memos' という名前で index.html テンプレートに渡してレンダリング
  return render_template('index.html', memos=memos_data)

# データ追加機能の実装（Create）
@app.route("/add", methods=['GET', 'POST'])
def add_memo():
   # case: GET request -> displat form
   if request.method == 'GET':
      return render_template('add_memo.html')
   # case: POST request -> データの処理とDB挿入
   elif request.method == 'POST':
      form_data = request.form
      # 作成日が空白の場合はNoneにする
      create_date = form_data.get('create_date')
      if create_date == '':
         create_date = None
        
      try:
         # Memoオブジェクトの作成
         new_memo = Memo(
            title=form_data['title'],
            content=form_data.get('content'),
            create_date=create_date
         )

         # データベース挿入関数を実行
         insert_memo(new_memo)

         return redirect(url_for('index'))
        # 登録後、メモリストのトップページにリダイレクト
        # (リダイレクト機能のために Flask から redirect と url_for のインポートが必要)
   
      except Exception as e:
        # エラー処理
        print(f"ERROR: メモの登録に失敗しました: {e}")
        return "登録エラーが発生しました", 500
      

# @app.route('/edit/', defaults={'memo_id': None}, methods=['GET', 'POST'])
@app.route('/edit/<int:memo_id>', methods=['GET', 'POST'])
def edit(memo_id):
   # データベースから対象のメモデータを取得
   memo_list = get_memo_by_id_or_title(identifier=memo_id)

   if not memo_list:
      return "エラー：指定されたメモが見つかりませんでした", 404
   
   # リストの最初の要素（メモオブジェクト/辞書）を取り出す
   memo_data = memo_list[0]
   
   # case: GET request -> edit form
   if request.method == 'GET':
      # テンプレートにメモデータを渡してレンダリング
      return render_template('edit_memo.html', memo=memo_data)
   # case: POST request -> データ処理とDB更新
   elif request.method == 'POST':
      new_title = request.form.get('title')
      new_content = request.form.get('content')
      # 値がNoneや空文字列の時、エラー処理
      if not new_title or not new_content:
         # エラーメッセージを返すか、元のフォームに戻す
         return "エラー： タイトルまたは本文が空です", 400
      # 念のためログに出力し、値がNULLや空になっていないか確認する
      print(f"DEBUG: Updating Memo ID {memo_id} with Title: {new_title}, Content: {new_content}")
      # update_memoが成功すればリダイレクトされる
      update_memo(memo_id, new_title, new_content)
      return redirect(url_for('index'))
   

@app.route('/delete/<int:memo_id>')
def delete(memo_id): # 指定されたIDの書籍を削除し、トップページにリダイレクト
   # データベース削除関数を実行
   success = delete_memo(memo_id)
   if not success:
      # 削除が失敗した場合、コンソールに警告を出すなど（ここでは簡略化）
      print(f"WARN: ID {memo_id} のメモの削除に失敗しました")

      return redirect(url_for('index'))
   # 削除後、書籍リストのトップページにリダイレクト

# 8. テストコード/実行ブロック