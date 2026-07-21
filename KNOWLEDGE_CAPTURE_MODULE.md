# Knowledge Capture Module Design

## Vision: Digital Apprenticeship System

**Problem**: Experienced engineers retire with 80% of critical knowledge undocumented — tacit knowledge, equipment quirks, vendor relationships, safety workarounds, and troubleshooting intuition that takes decades to develop.

**Solution**: A video-first knowledge capture system that records experts demonstrating live equipment walkthroughs, converts speech to searchable text, and builds a living knowledge repository.

## Core Workflow

```
Expert → Video Recording → Whisper Transcription → LLM Processing → Knowledge Base Integration
```

### 1. **Capture Interface** (`/capture` screen)
- **Live Video Recording**: WebRTC camera access for equipment walkthroughs
- **Screen + Audio**: Capture HMI screens, SCADA interfaces, technical drawings
- **Guided Prompts**: 
  - "Show me how you diagnose when Pump P-101A is cavitating"
  - "Walk through the startup sequence for Unit 200"
  - "What do you listen for during compressor rounds?"
- **Equipment Context**: Auto-tag with equipment IDs, locations, categories

### 2. **AI Processing Pipeline**
- **Whisper Integration**: Convert speech to high-accuracy text
- **LLM Enhancement**: 
  - Extract safety-critical steps
  - Identify equipment-specific knowledge
  - Generate structured procedures from informal explanations
  - Tag with relevant regulatory standards (OSHA, OISD, etc.)
- **Multi-modal Analysis**: Combine visual cues with audio explanations

### 3. **Knowledge Integration**
- **Auto-categorization**: Link to existing equipment in Asset Explorer
- **Cross-referencing**: Connect with existing incident reports, maintenance data
- **Searchable Repository**: Full-text search across all captured sessions
- **Progressive Enhancement**: Each capture improves the knowledge base

## Technical Implementation

### Frontend Components
```javascript
// KnowledgeCaptureScreen.jsx - new 7th screen
import React, { useState, useRef, useEffect } from 'react';

const KnowledgeCaptureScreen = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const recognitionRef = useRef(null);

    useEffect(() => {
        // Initialize Web Speech API
        if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            
            const recognition = recognitionRef.current;
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onresult = (event) => {
                let finalTranscript = '';
                let interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + ' ';
                    } else {
                        interimTranscript += transcript;
                    }
                }
                
                setTranscript(prev => prev + finalTranscript);
            };

            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
            };
        }
    }, []);

    const startRecording = () => {
        setTranscript('');
        setIsRecording(true);
        recognitionRef.current?.start();
    };

    const stopRecording = async () => {
        setIsRecording(false);
        recognitionRef.current?.stop();
        
        if (transcript.trim()) {
            setIsProcessing(true);
            await processWithLLM(transcript);
            setIsProcessing(false);
        }
    };

    const processWithLLM = async (text) => {
        try {
            const response = await fetch('/api/capture/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    transcript: text,
                    equipment_context: selectedEquipment,
                    session_type: 'procedure_walkthrough'
                })
            });
            
            const result = await response.json();
            // Handle processed knowledge...
        } catch (error) {
            console.error('LLM processing failed:', error);
        }
    };

    return (
        <div className="p-6 space-y-6">
            <div className="text-center">
                <h2 className="text-2xl font-bold mb-4">Knowledge Capture</h2>
                <p className="text-gray-600 mb-6">
                    Record equipment procedures and safety practices
                </p>
            </div>

            {/* Recording Controls */}
            <div className="flex justify-center space-x-4">
                {!isRecording ? (
                    <button 
                        onClick={startRecording}
                        className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg"
                    >
                        🎤 Start Recording
                    </button>
                ) : (
                    <button 
                        onClick={stopRecording}
                        className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg"
                    >
                        ⏹️ Stop & Process
                    </button>
                )}
            </div>

            {/* Live Transcript */}
            {isRecording && (
                <div className="bg-gray-100 p-4 rounded-lg">
                    <h3 className="font-semibold mb-2">Live Transcript:</h3>
                    <p className="text-gray-800">{transcript || "Listening..."}</p>
                </div>
            )}

            {/* Processing Status */}
            {isProcessing && (
                <div className="text-center">
                    <div className="spinner"></div>
                    <p>Processing with AI...</p>
                </div>
            )}
        </div>
    );
};
```

### Backend Extensions
```python
# api/knowledge_capture.py - new FastAPI endpoint
from fastapi import APIRouter, HTTPException
from groq import Groq
from pydantic import BaseModel

router = APIRouter()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class CaptureRequest(BaseModel):
    transcript: str
    equipment_context: str
    session_type: str

@router.post("/capture/process")
async def process_capture(request: CaptureRequest):
    """Process speech transcript into structured knowledge."""
    
    try:
        # Use your existing Groq LLM to structure the knowledge
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": KNOWLEDGE_EXTRACTION_PROMPT},
                {"role": "user", "content": f"""
Equipment: {request.equipment_context}
Session Type: {request.session_type}
Expert Transcript: {request.transcript}

Convert this expert explanation into structured procedure documentation.
                """}
            ]
        )
        
        structured_knowledge = response.choices[0].message.content
        
        # Store in your existing vector database
        await store_knowledge(structured_knowledge, request.equipment_context)
        
        return {
            "status": "success",
            "structured_knowledge": structured_knowledge,
            "message": "Knowledge captured and stored successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

async def store_knowledge(knowledge_text: str, equipment_context: str):
    """Store processed knowledge in ChromaDB using existing pipeline."""
    # Use your existing embedder to add to the knowledge base
    from ingestion.embedder import get_vector_store
    from langchain_core.documents import Document
    
    doc = Document(
        page_content=knowledge_text,
        metadata={
            "source": "expert_capture",
            "equipment": equipment_context,
            "category": "procedures",
            "document_type": "expert_knowledge"
        }
    )
    
    store = get_vector_store()
    store.add_documents([doc])
```

## Technical Implementation

### Speech-to-Text Options (100% Free)

#### **Option A: Browser Web Speech API** (Recommended)
```javascript
// Real-time speech recognition in the browser
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.continuous = true;
recognition.interimResults = true;
recognition.lang = 'en-US';

recognition.onresult = (event) => {
    let finalTranscript = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
        }
    }
    // Send to backend for LLM processing
    sendToLLM(finalTranscript);
};
```

### Speech-to-Text Comparison

| Feature | Web Speech API | Local Whisper |
|---|---|---|
| **Cost** | 100% Free | 100% Free |
| **Setup** | Zero setup | One-time model download |
| **Accuracy** | Very good | Excellent |
| **Latency** | Real-time | Near real-time |
| **Offline** | Requires internet | Fully offline |
| **Technical terms** | Good | Excellent |
| **Browser support** | Native | Requires audio upload |
| **Resource usage** | Minimal | CPU/GPU intensive |

**Recommendation**: Start with **Web Speech API** for immediate deployment, add local Whisper later for offline scenarios or higher accuracy needs.

#### **Option B: Local Whisper Model**
```python
# One-time model download (~1.5GB), then runs locally forever
import whisper

# Download once, use forever - no API costs
model = whisper.load_model("medium")  # or "large" for better accuracy

def transcribe_local(audio_file):
    result = model.transcribe(audio_file, language="english")
    return result["text"]
```

**Pros**:
- ✅ Completely offline
- ✅ No API key required
- ✅ High accuracy (especially for technical terms)
- ✅ One-time download, unlimited use

## Knowledge Extraction Prompts

### System Prompt for LLM Processing
```
You are an Industrial Knowledge Extraction AI. Process expert technician explanations and convert them into structured, searchable knowledge for training new engineers.

Extract:
1. **Safety-Critical Steps**: Any LOTO, PPE, hazard awareness points
2. **Equipment-Specific Knowledge**: Quirks, normal vs abnormal sounds/vibrations
3. **Troubleshooting Logic**: Diagnostic steps, what to check first
4. **Vendor/Parts Information**: Specific part numbers, supplier relationships  
5. **Regulatory Compliance**: References to OSHA, OISD, API standards
6. **Tacit Knowledge**: "Feel" indicators, experience-based judgments

Format as:
## Equipment: {equipment_tag}
## Procedure: {procedure_name}
## Safety Requirements: {critical_safety_steps}
## Step-by-step Instructions: {numbered_steps}
## Expert Tips: {tacit_knowledge_and_warnings}
## Related Standards: {regulatory_references}
## Troubleshooting: {diagnostic_indicators}
```

## Use Cases

### 1. **Equipment Walkthrough Capture**
- Senior engineer demonstrates compressor startup
- Camera captures gauge readings, valve positions
- Audio explains "normal" vs "concerning" sounds
- System auto-generates training SOP

### 2. **Troubleshooting Session Recording**
- Expert diagnoses unusual pump vibration
- Records thought process, diagnostic steps
- Captures root cause analysis methodology
- Builds troubleshooting decision trees

### 3. **Vendor Relationship Knowledge**
- Engineer explains preferred suppliers for critical parts
- Documents procurement lead times, quality issues
- Captures negotiation history, contact relationships
- Preserves supply chain institutional memory

### 4. **Safety Incident Learning**
- Post-incident walkthrough with safety engineer
- Documents lessons learned, procedure changes
- Links to existing incident reports in corpus
- Updates safety training materials

## Integration with Existing Modules

### Asset Explorer Integration
- **Equipment Linking**: Videos automatically tagged to asset hierarchy
- **Maintenance History**: Connect captures to work order patterns
- **Failure Correlation**: Link expert knowledge to historical failures

### Compliance Intel Integration
- **Regulatory Mapping**: Auto-tag procedures with relevant standards
- **Gap Identification**: Compare expert practices vs documented requirements
- **Audit Evidence**: Captured knowledge serves as compliance documentation

### AI Copilot Integration  
- **Enhanced Responses**: "Here's what Expert Engineer Smith demonstrated about this issue..."
- **Video Snippets**: Direct links to relevant captured segments
- **Progressive Learning**: System improves responses as more knowledge is captured

## Deployment Strategy

### Phase 1: MVP (2 weeks)
- Basic video upload + Whisper transcription
- Simple LLM processing for text extraction
- Manual categorization and tagging
- Single equipment type (pumps)

### Phase 2: Enhanced (4 weeks)
- Real-time video recording via webcam
- Automated equipment detection and tagging
- Integration with existing asset database
- Multi-equipment support

### Phase 3: Advanced (8 weeks)
- Live streaming with real-time transcription
- Computer vision for gauge reading, equipment identification
- Automated SOP generation from multiple captures
- Full integration with all existing modules

## ROI Calculation

**Problem Scale**: 
- Average industrial plant: 200 critical procedures
- 30% of experts retiring in next 5 years
- Cost of lost knowledge: $2-5M per critical expert departure

**Solution Value**:
- Knowledge preservation: Prevent 80% of knowledge loss
- Training acceleration: Reduce new hire ramp-up by 60%
- Standardization: Convert tribal knowledge to documented procedures
- Regulatory compliance: Automated documentation for audits

**Implementation Cost**: ~40 hours development + Whisper/compute costs
**Payback Period**: First expert departure prevented

## Technical Requirements

### Dependencies (All Free)
```txt
# No additional backend dependencies needed!
# Uses existing Groq LLM + ChromaDB + FastEmbed stack

# Optional: If you want local Whisper as backup
openai-whisper>=20231117  # Only if using local Whisper option
```

### Browser Compatibility (Web Speech API)
- ✅ Chrome 25+ (excellent support)  
- ✅ Edge 79+ (excellent support)
- ✅ Safari 14.1+ (good support)
- ✅ Firefox 100+ (basic support)

### Hardware Requirements
**For Web Speech API (Recommended)**:
- Any device with microphone
- Modern browser
- Internet connection (for initial page load only)

**For Local Whisper (Optional)**:
- CPU: Any modern processor (GPU optional but faster)
- RAM: 4GB+ available 
- Storage: 1.5GB for model download

## Integration Points

This module naturally extends your existing architecture:
- **Uses same RAG pipeline** for knowledge search/retrieval
- **Leverages existing Groq LLM** for processing transcripts
- **Builds on ChromaDB/FastEmbed** for semantic search of captured knowledge
- **Integrates with existing 6-screen dashboard** as 7th screen

The Knowledge Capture Module transforms your static document copilot into a **living, growing knowledge system** that captures the irreplaceable expertise of your most experienced people before it walks out the door.