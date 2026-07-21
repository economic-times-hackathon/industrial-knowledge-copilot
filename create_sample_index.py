"""
Quick sample index creator - adds a few synthetic industrial knowledge chunks
so the frontend has something to demonstrate with.
"""
import os
from dotenv import load_dotenv
load_dotenv()

# Set to use FastEmbed 
os.environ['EMBEDDING_BACKEND'] = 'fastembed'

from ingestion.embedder import get_vector_store
from langchain_core.documents import Document

# Sample industrial knowledge chunks
SAMPLE_CHUNKS = [
    {
        "text": "Process Safety Management (PSM) requires 14 elements including process hazard analysis, operating procedures, training, mechanical integrity, hot work permits, management of change, incident investigation, emergency planning, compliance audits, and contractor safety. OSHA PSM standard 1910.119 applies to processes with highly hazardous chemicals above threshold quantities.",
        "metadata": {
            "filename": "OSHA_PSM_Guidelines_3132.pdf",
            "category": "regulatory", 
            "source_url": "https://osha.gov/psl",
            "document_type": "REGULATORY",
            "description": "OSHA Process Safety Management Guidelines",
            "chunk_id": "sample_psm_001"
        }
    },
    {
        "text": "Centrifugal pump maintenance intervals: Daily - check for leaks, vibration, temperature; Weekly - monitor bearing temperatures, check coupling alignment; Monthly - inspect mechanical seals, check foundation bolts; Quarterly - vibration analysis, oil analysis; Annually - complete teardown inspection, bearing replacement if needed.",
        "metadata": {
            "filename": "Flowserve_Pump_IOM.pdf", 
            "category": "oem_manuals",
            "source_url": "manual-ref",
            "document_type": "OEM_MANUAL",
            "description": "Flowserve Pump Installation Operation Maintenance",
            "chunk_id": "sample_pump_001"
        }
    },
    {
        "text": "Confined space entry requires: Valid entry permit, atmospheric testing (oxygen 19.5-23.5%, LEL <10%, toxic gases <PEL), continuous ventilation, trained attendant outside, emergency rescue procedures, communication equipment, and fall protection if over 4 feet deep. Test atmosphere before entry and continuously during work.",
        "metadata": {
            "filename": "OSHA_Confined_Space_Standard.pdf",
            "category": "regulatory",
            "source_url": "https://osha.gov/confined-spaces", 
            "document_type": "REGULATORY",
            "description": "OSHA Confined Space Entry Requirements",
            "chunk_id": "sample_confined_001"
        }
    },
    {
        "text": "Pressure relief valve testing per API 576: Test safety valves every 5 years minimum, or more frequently based on service conditions. Pop test on test stand to verify set pressure +/- 3%. Inspect valve internals for corrosion, erosion, or damage. Ensure proper installation with adequate discharge piping and no backpressure exceeding 10% of set pressure.",
        "metadata": {
            "filename": "API_576_Relief_Valve_Standard.pdf",
            "category": "regulatory",
            "source_url": "api-standard",
            "document_type": "STANDARD", 
            "description": "API 576 Pressure Relief Valve Standard",
            "chunk_id": "sample_prv_001"
        }
    },
    {
        "text": "Emergency shutdown procedures: Sound general alarm, activate emergency shutdown systems, shut down all non-essential equipment, secure ignition sources, implement emergency response plan, account for all personnel at muster points, coordinate with emergency services, do not re-enter area until declared safe by incident commander.",
        "metadata": {
            "filename": "Emergency_Response_Procedures.pdf",
            "category": "incident_reports",
            "source_url": "internal-procedure",
            "document_type": "PROCEDURE",
            "description": "Plant Emergency Response Procedures", 
            "chunk_id": "sample_emergency_001"
        }
    }
]

def create_sample_index():
    """Create a minimal sample index for frontend testing."""
    print("Creating sample knowledge index...")
    
    # Get vector store (will create if doesn't exist)
    store = get_vector_store()
    
    # Convert to LangChain documents
    documents = []
    ids = []
    
    for chunk in SAMPLE_CHUNKS:
        doc = Document(
            page_content=chunk["text"],
            metadata=chunk["metadata"]
        )
        documents.append(doc)
        ids.append(chunk["metadata"]["chunk_id"])
    
    # Add to ChromaDB
    print(f"Adding {len(documents)} sample chunks...")
    store.add_documents(documents=documents, ids=ids)
    
    print("Sample index created successfully!")
    print("\nSample questions you can now ask:")
    print("- What is process safety management?")
    print("- How do you perform pump maintenance?") 
    print("- What are confined space entry requirements?")
    print("- Tell me about pressure relief valve testing")
    print("- What are emergency shutdown procedures?")

if __name__ == "__main__":
    create_sample_index()