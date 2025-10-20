# 1. ベースイメージを定義
FROM python:3.11-slim

# 2. コンテナ内の作業ディレクトリを定義
WORKDIR /app

# 3. ホストからコンテナへ依存ファイルのみコピー
COPY requirements.txt .

# 4. 依存ライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# 5. アプリケーションのソースコードをコピー
COPY . .

# 6. 環境変数やポートの定義、ランタイム設定
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000

# 7. コンテナ起動時に実行されるメインコマンド（例：Flaskサーバーの起動）を定義
CMD ["flask", "run"]
 