# 1. 必須インポート (Web操作に必要なものをすべて最初にインポート)
from flask import Flask

# 2. 環境変数のロードと取得

# 3. Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)

# 4. クラスの定義 (CRUD関数がこのクラスに依存するため、先に定義)

# 4-1. メモの情報を管理するクラス
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

# 6. データベース初期化の実行

# 7. Webルーティング
@app.route("/")
def index():
  return "<p>Hello, Flask</p>"

# 8. テストコード/実行ブロック