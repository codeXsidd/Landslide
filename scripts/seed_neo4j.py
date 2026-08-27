"""
NER-SAGE — Neo4j Seed Script
Creates the Road B demo scenario graph in Neo4j.
"""

import sys

from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "nersage_neo4j_pass"

def seed_neo4j():
    print("Connecting to Neo4j...")
    try:
        driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
        driver.verify_connectivity()
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")
        sys.exit(1)

    cypher_queries = [
        "MATCH (n) DETACH DELETE n;",  # Clear existing

        # Create Nodes
        "CREATE (v:Village {id: 'village_x', name: 'Village X', population: 850})",
        "CREATE (rb:Road {id: 'road_b', name: 'Road B', type: 'primary', status: 'OPEN'})",
        "CREATE (rc:Road {id: 'route_c', name: 'Route C', type: 'alternate', status: 'OPEN'})",
        "CREATE (j:Junction {id: 'junction_y', name: 'Junction Y'})",
        "CREATE (h:Hospital {id: 'hospital_z', name: 'Hospital Z'})",

        # Create Relationships
        "MATCH (v:Village {id: 'village_x'}), (rb:Road {id: 'road_b'}) CREATE (v)-[:CONNECTED_BY]->(rb)",
        "MATCH (v:Village {id: 'village_x'}), (rc:Road {id: 'route_c'}) CREATE (v)-[:CONNECTED_BY]->(rc)",
        "MATCH (rb:Road {id: 'road_b'}), (j:Junction {id: 'junction_y'}) CREATE (rb)-[:CONNECTS]->(j)",
        "MATCH (rc:Road {id: 'route_c'}), (j:Junction {id: 'junction_y'}) CREATE (rc)-[:CONNECTS]->(j)",
        "MATCH (j:Junction {id: 'junction_y'}), (h:Hospital {id: 'hospital_z'}) CREATE (j)-[:ACCESS_TO]->(h)",
    ]

    with driver.session() as session:
        for query in cypher_queries:
            session.run(query)

    print("Neo4j graph seeded successfully for Demo Scenario.")
    driver.close()

if __name__ == "__main__":
    seed_neo4j()
