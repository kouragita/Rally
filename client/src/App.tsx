import React, { useState } from 'react';
import { Layout } from './components/layout/Layout';
import { AnalysisForm } from './components/forms/AnalysisForm';
import { AnalysisQuery, AnalysisResult } from './services/types';
import './App.css';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<AnalysisResult | null>(null);

  const handleAnalysisSubmit = async (query: AnalysisQuery) => {
    setIsLoading(true);
    try {
      // TODO: Replace with your actual API call
      console.log('Submitting analysis:', query);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock result - replace with actual API response
      const mockResult: AnalysisResult = {
        id: '1',
        query: query.query,
        ecosystem: query.ecosystem || '',
        species: query.species,
        metrics: {
          temperatureChange: 2.3,
          precipitationChange: -15,
          speciesAtRisk: 47
        },
        insights: [
          'Arctic temperatures rising faster than global average',
          'Permafrost melting threatens ecosystem stability',
          'Species migration patterns shifting northward'
        ],
        charts: {
          temperature: [
            { name: '2020', value: 1.1 },
            { name: '2021', value: 1.4 },
            { name: '2022', value: 1.8 },
            { name: '2023', value: 2.1 },
            { name: '2024', value: 2.3 }
          ],
          population: [
            { name: 'Polar Bear', value: -23 },
            { name: 'Arctic Fox', value: -18 },
            { name: 'Caribou', value: -31 }
          ]
        },
        timestamp: new Date().toISOString()
      };
      
      setResults(mockResult);
    } catch (error) {
      console.error('Analysis failed:', error);
      // Handle error state
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Analysis Form - Takes 2/3 width */}
        <div className="lg:col-span-2">
          <AnalysisForm 
            onSubmit={handleAnalysisSubmit}
            isLoading={isLoading}
          />
          
          {/* Results will be displayed here */}
          {results && !isLoading && (
            <div className="mt-8">
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">
                  Analysis Results for: "{results.query}"
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-red-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-red-600">
                      +{results.metrics.temperatureChange}°C
                    </div>
                    <div className="text-sm text-gray-600">Temperature Change</div>
                  </div>
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {results.metrics.precipitationChange}%
                    </div>
                    <div className="text-sm text-gray-600">Precipitation Change</div>
                  </div>
                  <div className="bg-amber-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-amber-600">
                      {results.metrics.speciesAtRisk}
                    </div>
                    <div className="text-sm text-gray-600">Species at Risk</div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <h4 className="font-semibold text-gray-800">Key Insights:</h4>
                  {results.insights.map((insight, index) => (
                    <div key={index} className="flex items-start space-x-2">
                      <span className="text-blue-500 mt-1">•</span>
                      <span className="text-gray-700">{insight}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar - Takes 1/3 width */}
        <div className="space-y-6">
          <QuickStatsCard />
          <RecentAnalysesCard />
        </div>
      </div>
    </Layout>
  );
}

// Quick Stats Component
const QuickStatsCard: React.FC = () => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
    <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
      <span className="mr-2">📊</span>
      Global Climate Stats
    </h3>
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <span className="text-gray-600">Global Temp Rise</span>
        <span className="font-semibold text-red-600">+1.1°C</span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-gray-600">CO₂ Levels</span>
        <span className="font-semibold text-orange-600">421 ppm</span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-gray-600">Species Threatened</span>
        <span className="font-semibold text-red-600">41,415</span>
      </div>
    </div>
  </div>
);

// Recent Analyses Component
const RecentAnalysesCard: React.FC = () => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
    <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
      <span className="mr-2">📋</span>
      Recent Analyses
    </h3>
    <div className="space-y-3">
      <div className="p-3 bg-gray-50 rounded-lg">
        <div className="font-medium text-gray-800 text-sm">Arctic Ice Loss Impact</div>
        <div className="text-xs text-gray-500">2 hours ago</div>
      </div>
      <div className="p-3 bg-gray-50 rounded-lg">
        <div className="font-medium text-gray-800 text-sm">Coral Reef Bleaching</div>
        <div className="text-xs text-gray-500">1 day ago</div>
      </div>
      <div className="p-3 bg-gray-50 rounded-lg">
        <div className="font-medium text-gray-800 text-sm">Rainforest Deforestation</div>
        <div className="text-xs text-gray-500">3 days ago</div>
      </div>
    </div>
  </div>
);

export default App;
