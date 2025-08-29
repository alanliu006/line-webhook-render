# app.py
import os
from flask import Flask, request, abort

# 引入 line-bot-sdk 相關模組
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

app = Flask(__name__)

# 從環境變數取得 Channel Access Token 和 Channel Secret
# 這是部署到 Render 或其他平台時最推薦的做法，避免將機敏資訊寫死在程式碼中
channel_access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
channel_secret = os.environ.get('LINE_CHANNEL_SECRET')

# 確認 Channel Access Token 和 Channel Secret 是否已設定
if channel_access_token is None or channel_secret is None:
    print('請設定 LINE_CHANNEL_ACCESS_TOKEN 和 LINE_CHANNEL_SECRET 環境變數')
    # 在本地測試時，如果不想設定環境變數，可以暫時取消以下註解並填入您的資訊
    # channel_access_token = 'YOUR_CHANNEL_ACCESS_TOKEN'
    # channel_secret = 'YOUR_CHANNEL_SECRET'
    # exit(1) # 在正式部署時，如果沒有設定，應該要中斷程式

configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)

# 根目錄，用於基本測試
@app.route("/")
def home():
    return "伺服器運行中！"

# Webhook 的主要路徑
# *** 修正重點：同時允許 GET 和 POST 方法 ***
@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # 當 LINE Developers Console 按下 "Verify" 按鈕時，會發送 GET 請求
        # 我們只需要回傳一個 200 OK 的狀態碼即可
        return 'OK', 200
    
    elif request.method == 'POST':
        # 處理來自 LINE 的訊息事件
        signature = request.headers['X-Line-Signature']
        body = request.get_data(as_text=True)
        app.logger.info("Request body: " + body)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            print("簽名驗證失敗，請確認您的 Channel Secret 是否正確。")
            abort(400)
        except Exception as e:
            print(f"處理訊息時發生錯誤: {e}")
            abort(500)

        return 'OK'

# 處理文字訊息事件
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        # 取得使用者傳來的訊息
        user_message = event.message.text
        
        # *** 新功能：檢查特定訊息並回覆群組 ID ***
        if user_message == '群組ID':
            # 檢查訊息來源是否為群組
            if event.source.type == 'group':
                group_id = event.source.group_id
                reply_text = f"這個群組的 ID 是：\n{group_id}"
                
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=reply_text)]
                    )
                )
            else:
                # 如果不是在群組中，告知使用者
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="這個指令只能在群組中使用喔！")]
                    )
                )

# 伺服器啟動設定
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)