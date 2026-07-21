import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, Upload, AlertCircle, Camera, Image } from 'lucide-react';
import { api } from '../api';
import ErrorBanner from '../components/ErrorBanner';
import Spinner from '../components/Spinner';

const KnowledgeCaptureScreen = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [selectedEquipment, setSelectedEquipment] = useState('');
  const [attachedPhotos, setAttachedPhotos] = useState([]);
  const recognitionRef = useRef(null);
  const fileInputRef = useRef(null);
  const [speechSupported, setSpeechSupported] = useState(false);

  useEffect(() => {
    // Check Web Speech API support
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
      setSpeechSupported(true);
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      const recognition = recognitionRef.current;
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimText = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcriptPart = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcriptPart + ' ';
          } else {
            interimText += transcriptPart;
          }
        }
        
        if (finalTranscript) {
          setTranscript(prev => prev + finalTranscript);
        }
        setInterimTranscript(interimText);
      };

      recognition.onerror = (event) => {
        setError(`Speech recognition error: ${event.error}`);
        setIsRecording(false);
      };

      recognition.onend = () => {
        setIsRecording(false);
        setInterimTranscript('');
      };
    }
  }, []);

  const startRecording = () => {
    if (!selectedEquipment.trim()) {
      setError('Please select or enter equipment context first');
      return;
    }
    
    setTranscript('');
    setInterimTranscript('');
    setError('');
    setResult(null);
    setIsRecording(true);
    recognitionRef.current?.start();
  };

  const stopRecording = () => {
    setIsRecording(false);
    recognitionRef.current?.stop();
  };

  const processWithLLM = async () => {
    if (!transcript.trim()) {
      setError('No transcript available to process');
      return;
    }

    setIsProcessing(true);
    setError('');

    try {
      const response = await api.captureKnowledge({
        transcript: transcript.trim(),
        equipment_context: selectedEquipment,
        session_type: 'procedure_walkthrough',
        photos: attachedPhotos.map(p => p.data) // Include photo data
      });
      
      setResult(response);
      setTranscript(''); // Clear for next session
      setAttachedPhotos([]); // Clear photos
    } catch (err) {
      setError(err.message || 'Failed to process knowledge');
    } finally {
      setIsProcessing(false);
    }
  };

  const handlePhotoUpload = (event) => {
    const files = Array.from(event.target.files);
    
    files.forEach(file => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          setAttachedPhotos(prev => [...prev, {
            name: file.name,
            data: e.target.result
          }]);
        };
        reader.readAsDataURL(file);
      }
    });
  };

  const removePhoto = (index) => {
    setAttachedPhotos(prev => prev.filter((_, i) => i !== index));
  };

  const equipmentOptions = [
    'Pump P-101A/B',
    'Compressor C-201',
    'Heat Exchanger E-301',
    'Distillation Column T-401',
    'Reactor R-501'
  ];

  if (!speechSupported) {
    return (
      <div className="p-6 text-center">
        <AlertCircle className="mx-auto mb-4 text-red-500" size={48} />
        <h2 className="text-xl font-bold mb-2">Speech Recognition Not Supported</h2>
        <p className="text-gray-600">
          Your browser doesn't support Web Speech API. Please use Chrome, Edge, or Safari.
        </p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-4xl mx-auto">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Knowledge Capture</h2>
        <p className="text-gray-600">
          Record equipment procedures and troubleshooting knowledge
        </p>
      </div>

      {error && <ErrorBanner message={error} onDismiss={() => setError('')} />}

      {/* Equipment Selection */}
      <div className="bg-white rounded-lg border p-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Equipment Context
        </label>
        <select
          value={selectedEquipment}
          onChange={(e) => setSelectedEquipment(e.target.value)}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Select equipment...</option>
          {equipmentOptions.map(eq => (
            <option key={eq} value={eq}>{eq}</option>
          ))}
        </select>
        <input
          type="text"
          value={selectedEquipment}
          onChange={(e) => setSelectedEquipment(e.target.value)}
          placeholder="Or type custom equipment tag..."
          className="w-full mt-2 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Recording Controls */}
      <div className="flex justify-center space-x-4">
        {!isRecording ? (
          <button 
            onClick={startRecording}
            disabled={!selectedEquipment.trim()}
            className="flex items-center space-x-2 bg-red-500 hover:bg-red-600 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium"
          >
            <Mic size={20} />
            <span>Start Recording</span>
          </button>
        ) : (
          <button 
            onClick={stopRecording}
            className="flex items-center space-x-2 bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-medium"
          >
            <Square size={20} />
            <span>Stop Recording</span>
          </button>
        )}

        {transcript && !isRecording && (
          <button 
            onClick={processWithLLM}
            disabled={isProcessing}
            className="flex items-center space-x-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium"
          >
            <Upload size={20} />
            <span>Process Knowledge</span>
          </button>
        )}

        <button 
          onClick={() => fileInputRef.current?.click()}
          className="flex items-center space-x-2 bg-green-500 hover:bg-green-600 text-white px-4 py-3 rounded-lg font-medium"
        >
          <Camera size={20} />
          <span>Add Photos</span>
        </button>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          multiple
          onChange={handlePhotoUpload}
          className="hidden"
        />
      </div>

      {/* Recording Status */}
      {isRecording && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse mr-2"></div>
            <span className="font-medium text-red-800">Recording in progress...</span>
          </div>
          <p className="text-sm text-red-600">
            Speak clearly about the procedure, safety steps, or troubleshooting process.
          </p>
        </div>
      )}

      {/* Live Transcript */}
      {(transcript || interimTranscript) && (
        <div className="bg-gray-50 border rounded-lg p-4">
          <h3 className="font-semibold mb-2 text-gray-800">Transcript:</h3>
          <div className="text-gray-800 whitespace-pre-wrap">
            {transcript}
            <span className="text-gray-500 italic">{interimTranscript}</span>
          </div>
        </div>
      )}

      {/* Attached Photos */}
      {attachedPhotos.length > 0 && (
        <div className="bg-gray-50 border rounded-lg p-4">
          <h3 className="font-semibold mb-2 text-gray-800">Attached Photos ({attachedPhotos.length}):</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {attachedPhotos.map((photo, index) => (
              <div key={index} className="relative">
                <img 
                  src={photo.data} 
                  alt={photo.name}
                  className="w-full h-24 object-cover rounded border"
                />
                <button 
                  onClick={() => removePhoto(index)}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 text-xs hover:bg-red-600"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Processing Status */}
      {isProcessing && (
        <div className="text-center py-8">
          <Spinner />
          <p className="mt-4 text-gray-600">Processing with AI...</p>
          <p className="text-sm text-gray-500">Converting speech to structured knowledge...</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="font-semibold mb-2 text-green-800">✅ Knowledge Captured Successfully</h3>
          <div className="text-sm text-green-700">
            <p className="mb-2">Your expert knowledge has been:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Converted to structured procedures</li>
              <li>Tagged with equipment context</li>
              <li>Added to the searchable knowledge base</li>
              <li>Made available to all team members</li>
            </ul>
          </div>
          
          {result.structured_knowledge && (
            <details className="mt-4">
              <summary className="cursor-pointer text-green-800 font-medium">
                View Processed Knowledge
              </summary>
              <div className="mt-2 p-3 bg-white rounded border text-sm">
                <pre className="whitespace-pre-wrap">{result.structured_knowledge}</pre>
              </div>
            </details>
          )}
        </div>
      )}

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold mb-2 text-blue-800">How to Use</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Select the equipment you'll be discussing</li>
          <li>• Click "Start Recording" and speak naturally</li>
          <li>• Describe procedures, safety steps, or troubleshooting tips</li>
          <li>• Stop recording and process with AI to structure the knowledge</li>
          <li>• The system will add it to the searchable knowledge base</li>
        </ul>
      </div>
    </div>
  );
};

export default KnowledgeCaptureScreen;