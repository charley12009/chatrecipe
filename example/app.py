import openai,time,os,sys,functools,re,requests
from flask import Flask,request,abort
from linebot import LineBotApi,WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent,TextMessage,TextSendMessage
from argparse import ArgumentParser
from googlesearch import search

app = Flask(__name__)

line_bot_api = LineBotApi('9ekcCknLR58lCbAxpBv16tnoKi1t18IgMcuKbCRfAOx5lnsxnXbM/z68y4B90IlT77kzGMTfmh7XqjHJ4R//BlpWGcniwRSjRIwg6hfhGHCO7mnKidC/XQ9eoTtroHpiL6UVyNiCT/rCBIhSYKzPkwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('681c0d150a8a7aac1b5cf2bf5507848d')
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

def extract_keywords(input_text):
    # 在输入文本中查找匹配的关键词
    keywords = re.findall(r'請給我(.*?)的食譜', input_text)

    # 如果找到了关键词，返回第一个匹配结果
    if keywords:
        return keywords[0]
    else:
        return None
def search_google(query):
    api_key = "AIzaSyC3yoM21TBUKFKi8gomCCZK02M4GnFNIYE"  # 請換成您的 Google API 金鑰
    search_engine_id = "e3c44cc5ddf4041f3"  # 請換成您的 Custom Search Engine ID

    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={query}"
    response = requests.get(url)
    results = response.json()

    search_results = []
    if "items" in results:
        for item in results["items"]:
            search_results.append(item["link"])

    return search_results
# @functools.lru_cache(maxsize=None)
# def cached_search(query, num_results):
#     return search(query, num_results)

@handler.add(MessageEvent,message=TextMessage)
def message_text(event):
    #return "OK"
    search_result=[]
    def generate_answer(prompt):
        print('菜單或食譜生成中，請稍候...')
        response = openai.Completion.create(
            model="text-davinci-003",        
            prompt=prompt+'請用繁體中文，不要空行',
            temperature=0.3, #生成文字的多樣性，0~1，值越大，生成速度越慢
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
        if '@查詢當前食譜' in prompt:
            answer='使用說明: \nex:想知道牛肉麵的食譜，請輸入"請給我牛肉麵的食譜"'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=answer))
            break
        if '請給我' in prompt and '的食譜' in prompt:
            search_txt=extract_keywords(prompt)
            results = search_google(search_txt)
            
       # 將之前的答案和新的問題結合作為新的prompt
        prompt = f"{prev_answer} {prompt}"
        answer = generate_answer(prompt)
        answers=f'{answer}\n{results}'
        prev_answer = answer
        if results is True:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=answers))
        else:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=answer))
               
if __name__ == "__main__":
    app.run()
