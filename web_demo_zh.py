import gradio as gr
import mdtex2html
import pandas as pd
import random as rd
import os
import openai

def postprocess(self, y):
    if y is None:
        return []
    for i, (message, response) in enumerate(y):
        y[i] = (
            None if message is None else mdtex2html.convert((message)),
            None if response is None else mdtex2html.convert(response),
        )
    return y


gr.Chatbot.postprocess = postprocess


def parse_text(text):
    """copy from https://github.com/GaiZhenbiao/ChuanhuChatGPT/"""
    lines = text.split("\n")
    lines = [line for line in lines if line != ""]
    count = 0
    for i, line in enumerate(lines):
        if "```" in line:
            count += 1
            items = line.split('`')
            if count % 2 == 1:
                lines[i] = f'<pre><code class="language-{items[-1]}">'
            else:
                lines[i] = f'<br></code></pre>'
        else:
            if i > 0:
                if count % 2 == 1:
                    line = line.replace("`", "\`")
                    line = line.replace("<", "&lt;")
                    line = line.replace(">", "&gt;")
                    line = line.replace(" ", "&nbsp;")
                    line = line.replace("*", "&ast;")
                    line = line.replace("_", "&lowbar;")
                    line = line.replace("-", "&#45;")
                    line = line.replace(".", "&#46;")
                    line = line.replace("!", "&#33;")
                    line = line.replace("(", "&#40;")
                    line = line.replace(")", "&#41;")
                    line = line.replace("$", "&#36;")
                lines[i] = "<br>"+line
    text = "".join(lines)
    return text


def predict(input, chatbot, messages):
    chatbot.append((parse_text(input), ""))
    messages.append({"role": 'user', "content": input})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    response=completion.choices[0].message.content.strip()
    chatbot[-1] = (parse_text(input), parse_text(response))
    messages.append({"role": "assistant", "content": response})
    return chatbot, messages


def reset_user_input():
    return gr.update(value='')


def reset_state():
    global story
    global answer
    idx = rd.randint(0,question_num-1)
    story = table.values[idx,0].replace('\n', '')
    answer = table.values[idx,1].replace('\n', '')
    content = f"你是一个游戏，名叫海龟汤。\n\n你的游戏规则：你知道汤面和汤底，当用户需要玩海龟汤时，给予用户汤面，用户根据汤面提出问题，你判断用户的提问是否符合汤底的信息，除非用户猜到了汤底中的关键信息，你只能回答“是”和“否”。在用户提出的问题中包含汤底中的关键信息时，宣布游戏结束，并公布汤底。\n\n你的汤面是：“{story}”\n\n汤底是：“{answer}”\n\n接下来，当用户发出游戏请求，给出汤面，并通过回答“是”或“否”帮助用户猜到汤底。当用户提出的问题中包含汤底中的关键信息时，宣布游戏结束，并公布汤底。"

    chatbot = [("新的海龟汤", f"汤面：{story}\n\n你可以开始猜测汤底的内容，我会回答你的问题。请注意，我只能回答“是”或“否”。")]
    messages = [
        {"role": "system", "content": content},
        {"role": "user", "content": "陪我玩海龟汤。"},
        {"role": "assistant", "content": f"好的，以下是汤面：\n{story}\n\n你可以开始猜测汤底的内容，我会回答你的问题。请注意，我只能回答“是”或“否”。"},
    ]
    return chatbot, messages

def apply_apikey(apikey):
    openai.api_key = apikey
    return gr.update(value='')

table = pd.read_excel("data/puzzle_zh.xlsx")
question_num = table.values.shape[0]
idx = rd.randint(0,question_num-1)
story = table.values[idx,0].replace('\n', '')
answer = table.values[idx,1].replace('\n', '')
content = f"你是一个游戏，名叫海龟汤。\n\n你的游戏规则：你知道汤面和汤底，当用户需要玩海龟汤时，给予用户汤面，用户根据汤面提出问题，你判断用户的提问是否符合汤底的信息，除非用户猜到了汤底中的关键信息，你只能回答“是”和“否”。在用户提出的问题中包含汤底中的关键信息时，宣布游戏结束，并公布汤底。\n\n你的汤面是：“{story}”\n\n汤底是：“{answer}”\n\n接下来，当用户发出游戏请求，给出汤面，并通过回答“是”或“否”帮助用户猜到汤底。当用户提出的问题中包含汤底中的关键信息时，宣布游戏结束，并公布汤底。"

with gr.Blocks() as demo:
    gr.HTML("""<h1 align="center">海龟汤</h1>""")

    chatbot = gr.Chatbot([("新的海龟汤", f"汤面：{story}\n\n你可以开始猜测汤底的内容，我会回答你的问题。请注意，我只能回答“是”或“否”。")])
    with gr.Row():
        with gr.Column(scale=4):
            api_key = gr.Textbox(show_label=False, placeholder="OpenAI API Key", lines=1).style(
                container=False)
            apiBtn = gr.Button('Apply API key', variant="primary")
            with gr.Column(scale=12):
                user_input = gr.Textbox(show_label=False, placeholder="Input...", lines=10).style(
                    container=False)
            with gr.Column(min_width=32, scale=1):
                submitBtn = gr.Button("Submit", variant="primary")
            emptyBtn = gr.Button("New game")

    messages = gr.State([
        {"role": "system", "content": content},
        {"role": "user", "content": "陪我玩海龟汤。"},
        {"role": "assistant", "content": f"好的，以下是汤面：\n{story}\n\n你可以开始猜测汤底的内容，我会回答你的问题。请注意，我只能回答“是”或“否”。"},
    ])

    apiBtn.click(apply_apikey, [api_key], [api_key])

    submitBtn.click(predict, [user_input, chatbot, messages], [chatbot, messages],
                    show_progress=True)
    submitBtn.click(reset_user_input, [], [user_input])

    emptyBtn.click(reset_state, outputs=[chatbot, messages], show_progress=True)

demo.queue().launch(share=True, inbrowser=True)
