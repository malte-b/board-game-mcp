import gradio as gr
from utils.bgg import get_game_details, get_hot_games, search
from utils.recommend import recommend_similar

search_bgg = gr.Interface(
    fn=search,
    inputs=["text"],
    outputs="json",
    title="Board game geek search",
    description="Search for the board games from Board Game Geek"
)

game_details = gr.Interface(
    fn=get_game_details,
    inputs=["text"],
    outputs="json",
    title="Game Details",
    description="Get detailed information for board games (comma-separated IDs)"
)

hot_games = gr.Interface(
    fn=get_hot_games,
    inputs=[],
    outputs="json",
    title="Hot Games",
    description="Get the list of the top 50 trending games today on Board Game Geek"
)

recommend_games = gr.Interface(
    fn=recommend_similar,
    inputs=['text'],
    outputs=['json'],
    title='Recommended games',
    description='Get the list of recommended game'
)

bgg_tools = gr.TabbedInterface(
    [search_bgg, game_details, hot_games, recommend_games],
    ["Search", "Details", "Hot Games", "Recommend games"]
)


bgg_tools.launch(mcp_server=True)
