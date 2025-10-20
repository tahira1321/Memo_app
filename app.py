# 1. 必須インポート (Web操作に必要なものをすべて最初にインポート)
from flask import Flask

# 2. 環境変数のロードと取得

# 3. Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)

# 4. クラスの定義 (CRUD関数がこのクラスに依存するため、先に定義)

# 5. CRUD/データ操作関数

# 6. データベース初期化の実行

# 7. Webルーティング
@app.route("/")
def index():
  return "<p>Hello, Flask</p>"

# 8. テストコード/実行ブロック