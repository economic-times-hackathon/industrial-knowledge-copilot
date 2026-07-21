from neo4j import GraphDatabase
import os

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def get_neighbors(tag: str) -> list[str]:
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run(
                '''
                MATCH (a:Equipment {tag: $tag})-[:CONNECTED_TO]-(b:Equipment)
                RETURN b.tag as neighbor
                ''',
                tag=tag
            )
            neighbors = list(set([record["neighbor"] for record in result]))
        driver.close()
        return neighbors
    except Exception as e:
        print(f"Neo4j error: {e}")
        return []
