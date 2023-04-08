# -*- coding:utf-8 -*-
import os
import openai
import platform
import pandas as pd
import random as rd
openai.api_key = "your-openai-api-key"

os_name = platform.system()
clear_command = 'cls' if os_name == 'Windows' else 'clear'
table = pd.read_excel("data/puzzle_zh.xlsx")
question_num = table.values.shape[0]

while True:
    idx = rd.randint(0,question_num-1)
    story = table.values[idx,0].replace('\n', '')
    answer = table.values[idx,1].replace('\n', '')
    content = f"你是一个游戏，名叫海龟汤。\n\n你的游戏规则：你知道汤面和汤底，当用户需要玩海龟汤时，给予用户汤面，用户根据汤面提出问题，你判断用户的提问是否符合汤底的信息，除非用户猜到了汤底中的关键信息，你只能回答“是”和“否”。在用户提出的问题中包含汤底中的关键信息时，宣布游戏结束，并公布汤底。\n\n你的汤面是：“{story}”\n\n汤底是：“{answer}”\n\n接下来，当用户发出游戏请求，给出汤面，并通过回答“是”或“否”帮助用户猜到汤底。当用户提出的问题中包含汤底中的关键信息时，宣布游戏结束，并公布汤底。"

    messages = [
        {"role": "system", "content": content},
        {"role": "user", "content": "陪我玩海龟汤。"},
        {"role": "assistant", "content": f"好的，以下是汤面：\n{story}\n\n你可以开始猜测汤底的内容，我会回答你的问题。请注意，我只能回答“是”或“否”。"},
    ]
    print(f"汤面：{story}\n\n你可以开始猜测汤底的内容，我会回答你的问题。请注意，我只能回答“是”或“否”。\n\n输入'stop'停止游戏，输入'finish'完成游戏并进入下一轮。\n")
    while True:
        request = input("提问：")
        if request == 'stop' or request == 'finish':
            break
        messages.append({"role": "user", "content": request})
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        response=completion.choices[0].message.content.strip()
        print(f"回答：{response}")
        messages.append({"role": "assistant", "content": response})
    if request == 'stop':
        break
    else:
        os.system(clear_command)