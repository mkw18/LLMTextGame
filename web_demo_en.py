import gradio as gr
import mdtex2html
import pandas as pd
import random as rd
import os
import openai
openai.api_key = "your-openai-api-key"

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
    content = f"You are a Lateral Thinking Puzzle game. You will provide player a story, and the player will ask questions to guess the answer. You can only reply with 'Yes' or 'No'.\n\nThe story is: {story}\n\nThe answer is: {answer}\n\nNext, when a player ask you to play, you will tell the player about the story and let the player guess the answer. When the player reach the important element of the answer, end the game and tell the answer."

    chatbot = [("New Lateral Thinking Puzzle", f"Story: {story}\n\nYou can ask questions to get the answer. Notice that I can only reply with 'Yes' or 'No'.\n\nInput 'stop' to stop the game, 'finish' to finish the game and move on to next round.")]
    messages = [
        {"role": "system", "content": content},
        {"role": "user", "content": "Let's play a lateral thinking puzzle game!"},
        {"role": "assistant", "content": f"OK, I will provide a story, and you can ask questions to get the answer. The story is:\n{story}\n\nNotice that I can only reply with 'Yes' or 'No'."},
    ]
    return chatbot, messages


table = pd.read_excel("data/puzzle_en.xlsx")
question_num = table.values.shape[0]
idx = rd.randint(0,question_num-1)
story = table.values[idx,0]
answer = table.values[idx,1]
content = f"You are a Lateral Thinking Puzzle game. You will provide player a story, and the player will ask questions to guess the answer. You can only reply with 'Yes' or 'No'.\n\nThe story is: {story}\n\nThe answer is: {answer}\n\nNext, when a player ask you to play, you will tell the player about the story and let the player guess the answer. When the player reach the important element of the answer, end the game and tell the answer."

with gr.Blocks() as demo:
    gr.HTML("""<h1 align="center">Lateral Thinking Puzzle</h1>""")

    chatbot = gr.Chatbot([("New Lateral Thinking Puzzle", f"Story: {story}\n\nYou can ask questions to get the answer. Notice that I can only reply with 'Yes' or 'No'.\n\nInput 'stop' to stop the game, 'finish' to finish the game and move on to next round.")])
    with gr.Row():
        with gr.Column(scale=4):
            with gr.Column(scale=12):
                user_input = gr.Textbox(show_label=False, placeholder="Input...", lines=10).style(
                    container=False)
            with gr.Column(min_width=32, scale=1):
                submitBtn = gr.Button("Submit", variant="primary")
            emptyBtn = gr.Button("New game")

    messages = gr.State([
        {"role": "system", "content": content},
        {"role": "user", "content": "Let's play a lateral thinking puzzle game!"},
        {"role": "assistant", "content": f"OK, I will provide a story, and you can ask questions to get the answer. The story is:\n{story}\n\nNotice that I can only reply with 'Yes' or 'No'."},
    ])

    submitBtn.click(predict, [user_input, chatbot, messages], [chatbot, messages],
                    show_progress=True)
    submitBtn.click(reset_user_input, [], [user_input])

    emptyBtn.click(reset_state, outputs=[chatbot, messages], show_progress=True)

demo.queue().launch(share=True, inbrowser=True)
