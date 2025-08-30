import { useState, useEffect } from 'react';
import * as api from './services/api';

interface Ecosystem {
  id: number;
  name: string;
  type: string;
  description: string;
}

interface Species {
  id: number;
  scientific_name: string;
  common_name: string;
}

interface Report {
  id: number;
  report_type: string;
  query_parameters: any;
  analysis_results: any;
  predictions: any;
  citations: any;
  confidence_scores: any;
  ai_model_version: string;
  generated_at: string;
}

function App() {
  const [ecosystems, setEcosystems] = useState<Ecosystem[]>([]);
  const [species, setSpecies] = useState<Species[]>([]);
  const [selectedEcosystem, setSelectedEcosystem] = useState<string>('');
  const [selectedSpecies, setSelectedSpecies] = useState<string>('');
  const [query, setQuery] = useState<string>('');
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const ecoData = await api.getEcosystems();
        setEcosystems(ecoData);
        const speciesData = await api.getSpecies();
        setSpecies(speciesData);
      } catch (err) {
        setError('Failed to fetch initial data.');
        console.error(err);
      }
    };
    fetchData();
  }, []);

  const handleAnalysis = async (targetType: 'ecosystem' | 'species') => {
    setLoading(true);
    setError(null);
    setReport(null);
    try {
      let targetName = '';
      let targetId: number | undefined;

      if (targetType === 'ecosystem') {
        targetName = selectedEcosystem;
        const eco = ecosystems.find(e => e.name === selectedEcosystem);
        targetId = eco?.id;
      } else {
        targetName = selectedSpecies;
        const sp = species.find(s => s.scientific_name === selectedSpecies);
        targetId = sp?.id;
      }

      if (!targetName) {
        setError('Please select a target.');
        setLoading(false);
        return;
      }

      const analysisPayload = {
        query,
        target_type: targetType,
        target_name: targetName,
        target_id: targetId,
      };

      const { report_id } = await api.triggerAnalysis(analysisPayload);
      const fetchedReport = await api.getReport(report_id);
      setReport(fetchedReport);
    } catch (err) {
      setError('Failed to generate report.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">Climate & Wildlife AI Dashboard</h1>

      <div className="max-w-4xl mx-auto bg-white p-6 rounded-lg shadow-md mb-8">
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">Run New Analysis</h2>
        
        <div className="mb-4">
          <label htmlFor="query" className="block text-gray-700 text-sm font-bold mb-2">Query:</label>
          <input
            type="text"
            id="query"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            placeholder="e.g., Main threats to Arctic Terrestrial Systems"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>

        <div className="mb-4">
          <label htmlFor="ecosystem-select" className="block text-gray-700 text-sm font-bold mb-2">Select Ecosystem:</label>
          <select
            id="ecosystem-select"
            className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            value={selectedEcosystem}
            onChange={(e) => setSelectedEcosystem(e.target.value)}
          >
            <option value="">-- Select an Ecosystem --</option>
            {ecosystems.map((eco) => (
              <option key={eco.id} value={eco.name}>{eco.name}</option>
            ))}
          </select>
          <button
            onClick={() => handleAnalysis('ecosystem')}
            className="mt-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            disabled={loading}
          >
            {loading ? 'Analyzing...' : 'Analyze Ecosystem'}
          </button>
        </div>

        <div className="mb-4">
          <label htmlFor="species-select" className="block text-gray-700 text-sm font-bold mb-2">Select Species:</label>
          <select
            id="species-select"
            className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            value={selectedSpecies}
            onChange={(e) => setSelectedSpecies(e.target.value)}
          >
            <option value="">-- Select a Species --</option>
            {species.map((sp) => (
              <option key={sp.id} value={sp.scientific_name}>{sp.scientific_name} ({sp.common_name})</option>
            ))}
          </select>
          <button
            onClick={() => handleAnalysis('species')}
            className="mt-2 bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            disabled={loading}
          >
            {loading ? 'Analyzing...' : 'Analyze Species'}
          </button>
        </div>

        {error && <p className="text-red-500 text-center mb-4">Error: {error}</p>}
      </div>

      {report && (
        <div className="max-w-4xl mx-auto bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">Analysis Report (ID: {report.id})</h2>
          <p className="text-gray-600 mb-2">**Query:** {report.report_type}</p>
          <p className="text-gray-600 mb-2">**AI Model:** {report.ai_model_version}</p>
          <p className="text-gray-600 mb-2">**Confidence:** {(report.confidence_scores?.overall * 100).toFixed(2)}%</p>
          
          <h3 className="text-xl font-semibold text-gray-700 mt-4 mb-2">Summary:</h3>
          <p className="text-gray-600 mb-4">{report.analysis_results?.raw_text}</p>

          {report.predictions && Object.keys(report.predictions).length > 0 && (
            <div className="mt-4">
              <h3 className="text-xl font-semibold text-gray-700 mb-2">Predictions:</h3>
              {Object.entries(report.predictions).map(([key, value]) => (
                <p key={key} className="text-gray-600 mb-1">**{key}:** {value}</p>
              ))}
            </div>
          )}

          {report.citations && Object.keys(report.citations).length > 0 && (
            <div className="mt-4">
              <h3 className="text-xl font-semibold text-gray-700 mb-2">Citations:</h3>
              {Object.entries(report.citations).map(([key, value]) => (
                <p key={key} className="text-gray-600 mb-1">**{key}:** {value}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
