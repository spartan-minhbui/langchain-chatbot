from typing import Any
import gradio as gr

from chatbot.bot import Bot
from chatbot.common.config import Config
from chatbot.memory import MongoChatbotMemory


class BaseGradioUI:
    def __init__(
            self,
            config: Config = None,
            bot: Bot = None
    ):
        self.config = config if config is not None else Config()
        self.bot = bot if bot is not None else Bot(config=self.config, memory_class=MongoChatbotMemory)

    def init(self):
        self.bot.init()

    @staticmethod
    def user_state(message: str, chat_history: Any):
        """Initiate user state and chat history

        Args:
            message (str): user message
            chat_history (Any): chat history
        """

        return "", chat_history + [[message, None]]

    def load_chat_history(self, chat_history: Any):
        self.bot.reset_history()
        memory = self.bot.chain.memory.chat_memory
        for history in chat_history[:-1]:
            memory.add_user_message(history[0])
            memory.add_ai_message(history[1])

    def respond(self, chat_history):
        message = chat_history[-1][0]
        self.load_chat_history(chat_history)
        result = self.bot.predict(sentence=message)
        chat_history[-1][-1] = result[0].message
        return chat_history

    def start_demo(self, port=8000, debug=False, share=True):
        with gr.Blocks() as demo:
            gr.Markdown("""<h1><center> LLM Assistant </center></h1>""")
            chatbot = gr.Chatbot(label="Assistant").style(height=700)

            with gr.Row():
                message = gr.Textbox(show_label=False,
                                     placeholder="Enter your prompt and press enter",
                                     visible=True)
            message.submit(
                self.user_state,
                [message, chatbot],
                [message, chatbot],
                queue=False
            ).then(
                self.respond,
                inputs=chatbot,
                outputs=chatbot
            )

        demo.queue()
        demo.launch(debug=debug, server_port=port, share=share)