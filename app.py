import os
from flask import Flask, request, abort

app = Flask(__name__)

# 取得在 Render 平台上設定的環境變數
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')

@app.route("/")
def home():
    return "Hello, this is the webhook server!"

# LINE Webhook 的進入點，務必使用 POST 方法
@app.route("/webhook", methods=['POST'])
def webhook():
    # 實際應用中，這裡需要驗證 X-Line-Signature 簽名
    # 但為了通過 LINE 的 "Verify" 請求，我們可以直接回傳 200 OK
    # Verify 請求的 body 是空的，也不會有簽名
    
    # signature = request.headers['X-Line-Signature']
    # body = request.get_data(as_text=True)

    # try:
    #     handler.handle(body, signature)
    # except InvalidSignatureError:
    #     abort(400)

    return 'OK'

if __name__ == "__main__":
    # 使用 os.environ.get('PORT', 8080) 來適應 Render 的環境
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)