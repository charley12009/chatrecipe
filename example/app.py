import openai
import time
from flask import Flask,request,abort
from linebot import LineBotApi,WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent,TextMessage,TextSendMessage
from argparse import ArgumentParser
app = Flask(__name__)
line_bot_api = LineBotApi('+7yuhcMAoKKgtTNHkvBZDp58T0kRkTj5BHSf1xcPhEezjBDr7p2+akYlDQJsZB1t77kzGMTfmh7XqjHJ4R//BlpWGcniwRSjRIwg6hfhGHD7oApBOP102duL4DiuSm49DruxSKI3dOdtHZ1RjIJMYwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('6bf3923734819f11b70abf9d4fcff387')
openai.api_key = "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"
@app.route("/callback",methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: "+body)
    try:
        handler.handle(body,signature)
    except:
        print("Invalid sugnature, Please check yoy channel access token/channel secret")
        abort(400)
    return 'OK'
@handler.add(MessageEvent,message=TextMessage)
def hanle_message(event):
    #return "OK"
    prompt=event.message.text
    def generate_answer(prompt):
        print('菜單或食譜生成中，請稍候...')
        response = openai.Completion.create(
            model="text-davinci-003",        
            prompt=prompt+'請用繁體中文，不要空行',
            temperature=0.1, #生成文字的多樣性，0~1，值越大，生成速度越慢
            max_tokens=1024, #輸出最多字數
            n=1,
            stop=None,
            echo=False,
            presence_penalty=0.5,
            top_p=0.1,
        )
        answer = response.choices[0].text.replace('\n\n', '\n')  
        return answer

    prev_answer = ""  # 初始化之前的答案為空

    while True:
        prompt = input("請輸入您的問題（或輸入 q 結束程式）：")
        #prompt+='請用繁體中文回答'
        if prompt == "q":
            break
        if '菜單' in prompt:
            prompt += '只要餐點名稱'
        if '食譜' in prompt:
            prompt += '輸出內容包括餐點名稱、材料、餐點做法，材料中要包含數量'
        # 將之前的答案和新的問題結合作為新的prompt
        prompt = f"{prev_answer} {prompt}"
        start_time=time.time()
        answer = generate_answer(prompt)
    
        end_time = time.time()  # 記錄結束時間
        elapsed_time = end_time - start_time  # 計算花費的時間
        print(f'花費時間{elapsed_time}')
        prev_answer = answer
        #print(answer)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=answer))
        #return "OK"
        #print('上述建議僅供參考，可依個人需求調整')
        # 將新的回答作為之前的答案，供下一次迭代使用
        
import os
if __name__ == "__main__":
    #arg_parser = ArgumentParser(
    #    usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    #)
    #arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    #arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    #options = arg_parser.parse_args()

    app.run()
    #debug=options.debug, port=options.port
