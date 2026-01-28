# titan_bot.py
from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.pgvector import PgVector
from agno.db.postgres import PostgresDb
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.csv_toolkit import CsvTools
from agno.tools.calculator import CalculatorTools
from agno.tools.reasoning import ReasoningTools
from agno.team import Team

from config import db_url, model, embedder
from instructions import *

warframe_knowledge = Knowledge(
    vector_db=PgVector(table_name="warframe_vectors", db_url=db_url, embedder=embedder),
    contents_db=PostgresDb(id="warframe_contents_db", db_url=db_url, knowledge_table="warframe_contents"),
)

clan_knowledge = Knowledge(
    vector_db=PgVector(table_name="clan_vectors", db_url=db_url, embedder=embedder),
    contents_db=PostgresDb(id="clan_contents_db", db_url=db_url, knowledge_table="clan_contents"),
)

warframe_agent = Agent(
    name="Warframe Agent",
    model=model,
    knowledge=warframe_knowledge,
    tools=[CalculatorTools()],
    search_knowledge=True,
    add_knowledge_to_context=True,
    instructions=WARFRAME_AGENT_INSTRUCTIONS,
)

clan_agent = Agent(
    name="Clan Agent",
    model=model,
    knowledge=clan_knowledge,
    search_knowledge=True,
    instructions=CLAN_AGENT_INSTRUCTIONS,
)

riven_agent = Agent(
    name="Riven Agent",
    model=model,
    tools=[
        ReasoningTools(add_instructions=True),
        CsvTools(csvs=["csv/riven_sales.csv", "csv/weapon_info.csv"]),
        CalculatorTools()
    ],
    instructions=RIVEN_AGENT_INSTRUCTIONS,
    markdown=True,
)

web_search_agent = Agent(
    name="Web Search Agent",
    model=model,
    tools=[DuckDuckGoTools()],
    instructions=["Recherche sur le web pour les actualités Warframe récentes."]
)

titan_bot_team = Team(
    name="Titans AI Core",
    agents=[warframe_agent, clan_agent, riven_agent, web_search_agent],
    instructions=TITAN_BOT_INSTRUCTIONS,
)
