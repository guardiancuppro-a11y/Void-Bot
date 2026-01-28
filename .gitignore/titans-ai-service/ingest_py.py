# ingest_knowledge.py
import os
from agno.knowledge.reader.text_reader import TextReader
from agno.knowledge.reader.csv_reader import CSVReader
from titan_bot import warframe_knowledge, clan_knowledge

def load_knowledge():
    print("🚀 Ingestion de la base de connaissances...")
    if os.path.exists("knowledge/warframe"):
        warframe_knowledge.load_documents(path="knowledge/warframe", reader=TextReader(chunk=True))
    if os.path.exists("knowledge/clan"):
        clan_knowledge.load_documents(path="knowledge/clan", reader=TextReader(chunk=True))
    print("✅ Ingestion terminée !")

if __name__ == "__main__":
    load_knowledge()
