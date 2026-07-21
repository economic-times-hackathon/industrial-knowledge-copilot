from neo4j import GraphDatabase

EQUIPMENT_GRAPH = {
    "TK-001": ["P-101A"],
    "P-101A": ["TK-001", "E-101", "FIC-101"],
    "FIC-101": ["P-101A"],
    "E-101": ["P-101A", "F-101", "CT-401"],
    "F-101": ["E-101", "V-101", "TIC-205"],
    "TIC-205": ["F-101"],
    "V-101": ["F-101", "E-201", "B-101", "PSV-101"],
    "PSV-101": ["V-101"],
    "E-201": ["V-101", "V-601", "CT-401"],
    "V-601": ["E-201", "P-201A"],
    "P-201A": ["V-601"],
    "B-101": ["V-101"],
    "R-601": ["K-601"],
    "K-601": ["R-601"],
    "CT-401": ["E-101", "E-201"]
}

def seed_database(uri, user, password):
    print(f"Connecting to {uri}...")
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Clear existing data
        session.run("MATCH (n) DETACH DELETE n")
        
        # Create nodes
        for tag in EQUIPMENT_GRAPH.keys():
            session.run("CREATE (:Equipment {tag: $tag})", tag=tag)
            
        # Create relationships
        for tag, neighbors in EQUIPMENT_GRAPH.items():
            for neighbor in neighbors:
                session.run(
                    '''
                    MATCH (a:Equipment {tag: $tag})
                    MATCH (b:Equipment {tag: $neighbor})
                    MERGE (a)-[:CONNECTED_TO]->(b)
                    ''',
                    tag=tag, neighbor=neighbor
                )
    
    driver.close()
    print("Graph seeded successfully.")

if __name__ == "__main__":
    seed_database("bolt://localhost:7687", "neo4j", "password")
