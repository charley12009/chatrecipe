import openai
import time
from flask import Flask,request,abort
from linebot import LineBotApi,WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent,TextMessage,TextSendMessage
from argparse import ArgumentParser
import os
import sys
app = Flask(__name__)


line_bot_api = LineBotApi('9ekcCknLR58lCbAxpBv16tnoKi1t18IgMcuKbCRfAOx5lnsxnXbM/z68y4B90IlT77kzGMTfmh7XqjHJ4R//BlpWGcniwRSjRIwg6hfhGHCO7mnKidC/XQ9eoTtroHpiL6UVyNiCT/rCBIhSYKzPkwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('681c0d150a8a7aac1b5cf2bf5507848d')
#channel_secret = os.getenv('681c0d150a8a7aac1b5cf2bf5507848d',None)
#channel_access_token = os.getenv('DDaU36i0rAtuGKLdiHToihqW1/uUiNccZCZ93CjFe2UU5OJzGlUJL17L6cIfDRaA77kzGMTfmh7XqjHJ4R//BlpWGcniwRSjRIwg6hfhGHCdoWbxC2/GTUpWRMleLVdmtBOOOJhBxWWUwrIusYFZiAdB04t89/1O/w1cDnyilFU=',None)
#if channel_secret is None:
#    print('Specify LINE_CHANNEL_SECRET as environment variable.')
#    sys.exit(1)
#if channel_access_token is None:
#    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
#    sys.exit(1)

#line_bot_api = LineBotApi(channel_access_token)
#handler = WebhookHandler(channel_secret)

openai.api_key = "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"

@app.route("/callback",methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: "+body)
    print(body)
    try:
        handler.handle(body,signature)
    except InvalidSignatureError:
        print("Invalid sugnature, Please check yoy channel access token/channel secret")
        abort(400)
    return 'OK'

@handler.add(MessageEvent,message=TextMessage)
def message_text(event):
    #return "OK"
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

        

    while True:
        prompt=event.message.text
        prev_answer = ""  # 初始化之前的答案為空
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
        #print(f'花費時間{elapsed_time}')
        prev_answer = answer
       #print(answer)
        #if event.source.user_id != "U1df0b1870f9fd24fb2b2871cf95d4ca7":
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=answer))
    #return 'OK'

        #return "OK"
        #print('上述建議僅供參考，可依個人需求調整')
        # 將新的回答作為之前的答案，供下一次迭代使用
        
if __name__ == "__main__":
    
        #arg_parser = ArgumentParser(
    #    usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    #)
    #arg_parser.add_argument('-p', '--port', type=int, default=5000, help='port')
    #arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    #options = arg_parser.parse_args()

    app.run()
    #debug=options.debug, port=options.port
