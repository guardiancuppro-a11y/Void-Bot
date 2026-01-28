# start.py
import os
from agno.os import AgentOS
from agno.knowledge.reader.text_reader import TextReader
from titan_bot import titan_bot_team, warframe_knowledge, clan_knowledge
from agno.db.postgres import PostgresDb
from config import db_url

tracing_db = PostgresDb(db_url=db_url, id="tracing_db")

agent_os = AgentOS(
    id="titan-bot-os",
    teams=[titan_bot_team],
    tracing=True,
    db=tracing_db,
)

app = agent_os.get_app()

if __name__ == "__main__":
    print("🚀 Initialisation des bases de connaissances...")
    if os.path.exists("knowledge/warframe"):
        warframe_knowledge.add_content(path="knowledge/warframe", skip_if_exists=True, reader=TextReader(chunk=True))
    if os.path.exists("knowledge/clan"):
        clan_knowledge.add_content(path="knowledge/clan", skip_if_exists=True, reader=TextReader(chunk=True))
    
    agent_os.serve(app="start:app", port=8000)
