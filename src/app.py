import gradio as gr
from utils.bgg import search


search_bgg = gr.Interface(
    fn=search,
    inputs=["text"],
    outputs="json",
    title="Board game geek search",
    description="Search for the board games from Board Game Geek"
)

search_bgg.launch(mcp_server=True)
