# -*- coding:utf-8 -*-
import os
import openai
import platform
import pandas as pd
import random as rd
openai.api_key = "your-openai-api-key"

os_name = platform.system()
clear_command = 'cls' if os_name == 'Windows' else 'clear'
table = pd.read_excel("data/puzzle_en.xlsx")
question_num = table.values.shape[0]

while True:
    idx = rd.randint(0,question_num-1)
    story = table.values[idx,0]
    answer = table.values[idx,1]
    content = f"You are a Lateral Thinking Puzzle game. You will provide player a story, and the player will ask questions to guess the answer. You can only reply with 'Yes' or 'No'.\n\nThe story is: {story}\n\nThe answer is: {answer}\n\nNext, when a player ask you to play, you will tell the player about the story and let the player guess the answer. When the player reach the important element of the answer, end the game and tell the answer."

    messages = [
        {"role": "system", "content": content},
        {"role": "user", "content": "Let's play a lateral thinking puzzle game!"},
        {"role": "assistant", "content": f"OK, I will provide a story, and you can ask questions to get the answer. The story is:\n{story}\n\nNotice that I can only reply with 'Yes' or 'No'."},
    ]
    print(f"Story: {story}\n\nYou can ask questions to get the answer. Notice that I can only reply with 'Yes' or 'No'.\n\nInput 'stop' to stop the game, 'finish' to finish the game and move on to next round.\n")
    while True:
        request = input("question: ")
        if request == 'stop' or request == 'finish':
            break
        messages.append({"role": "user", "content": request})
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        response=completion.choices[0].message.content.strip()
        print(f"answer: {response}")
        messages.append({"role": "assistant", "content": response})
    if request == 'stop':
        break
    else:
        os.system(clear_command)