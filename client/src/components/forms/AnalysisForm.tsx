import React, { useState } from 'react';
import { Card, CardHeader, CardBody } from '../ui/Card';
import { Dropdown } from '../ui/Dropdown';
import { Input } from '../ui/Input';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { ECOSYSTEM_OPTIONS, SPECIES_OPTIONS } from '../../utils/constants';
import { AnalysisQuery } from '../../services/types';

interface AnalysisFormProps {
  onSubmit: (query: AnalysisQuery) => void;
  isLoading?: boolean;
}

export const AnalysisForm: React.FC<AnalysisFormProps> = ({
  onSubmit,
  isLoading = false
}) => {
  const [query, setQuery] = useState('');
  const [selectedEcosystem, setSelectedEcosystem] = useState('');
  const [selectedSpecies, setSelectedSpecies] = useState('');
  const [analysisType, setAnalysisType] = useState<'ecosystem' | 'species'>('ecosystem');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const availableSpecies = SPECIES_OPTIONS.filter(
    species => species.ecosystemId === selectedEcosystem
  );

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!query.trim()) {
      newErrors.query = 'Please enter a research query';
    }
    
    if (analysisType === 'ecosystem' && !selectedEcosystem) {
      newErrors.ecosystem = 'Please select an ecosystem';
    }
    
    if (analysisType === 'species' && !selectedSpecies) {
      newErrors.species = 'Please select a species';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (!validateForm()) return;
    
    const analysisQuery: AnalysisQuery = {
      query: query.trim(),
      analysisType,
      ecosystem: selectedEcosystem || undefined,
      species: selectedSpecies || undefined,
    };
    
    onSubmit(analysisQuery);
  };

  const handleAnalysisTypeChange = (type: 'ecosystem' | 'species') => {
    setAnalysisType(type);
    setErrors({});
    if (type === 'ecosystem') {
      setSelectedSpecies('');
    }
  };

  if (isLoading) {
    return (
      <Card>
        <LoadingSpinner 
          message="Analyzing Environmental Data..." 
          subMessage="Processing climate patterns and wildlife impacts"
        />
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader
        title="Run New Analysis"
        subtitle="Analyze climate impacts on wildlife ecosystems"
        icon="🔍"
      />
      
      <CardBody className="space-y-6">
        <Input
          label="Research Query"
          icon="🎯"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., Main threats to Arctic Terrestrial Systems"
          helperText="Describe the environmental challenge you want to analyze"
          error={errors.query}
        />

        <div className="space-y-4">
          <label className="block text-sm font-semibold text-gray-700">
            Analysis Type
          </label>
          <div className="flex space-x-4">
            <AnalysisTypeButton
              type="ecosystem"
              label="Analyze Ecosystem"
              icon="🌿"
              active={analysisType === 'ecosystem'}
              onClick={() => handleAnalysisTypeChange('ecosystem')}
            />
            <AnalysisTypeButton
              type="species"
              label="Analyze Species"
              icon="🦌"
              active={analysisType === 'species'}
              onClick={() => handleAnalysisTypeChange('species')}
            />
          </div>
        </div>

        <div className="space-y-2">
          <Dropdown
            options={ECOSYSTEM_OPTIONS}
            value={selectedEcosystem}
            onChange={setSelectedEcosystem}
            placeholder="Choose ecosystem type..."
            icon="🏔️"
            error={errors.ecosystem}
          />
          {errors.ecosystem && (
            <p className="text-sm text-red-600">{errors.ecosystem}</p>
          )}
        </div>

        {analysisType === 'species' && (
          <div className="space-y-2">
            <Dropdown
              options={availableSpecies}
              value={selectedSpecies}
              onChange={setSelectedSpecies}
              placeholder="Select species to focus on..."
              icon="🐾"
              disabled={!selectedEcosystem}
              error={errors.species}
            />
            {errors.species && (
              <p className="text-sm text-red-600">{errors.species}</p>
            )}
            {!selectedEcosystem && (
              <p className="text-xs text-gray-500">Select an ecosystem first to see available species</p>
            )}
          </div>
        )}

        <div className="flex space-x-4 pt-4">
          <button 
            onClick={handleSubmit}
            className="flex-1 btn-primary flex items-center justify-center"
            disabled={isLoading}
          >
            <span className="mr-2">🚀</span>
            {analysisType === 'ecosystem' ? 'Analyze Ecosystem' : 'Analyze Species'}
          </button>
          
          <button 
            type="button"
            className="btn-secondary flex items-center"
            onClick={() => {
              setQuery('');
              setSelectedEcosystem('');
              setSelectedSpecies('');
              setErrors({});
            }}
          >
            <span className="mr-2">🔄</span>
            Reset
          </button>
        </div>
      </CardBody>
    </Card>
  );
};

interface AnalysisTypeButtonProps {
  type: 'ecosystem' | 'species';
  label: string;
  icon: string;
  active: boolean;
  onClick: () => void;
}

const AnalysisTypeButton: React.FC<AnalysisTypeButtonProps> = ({
  label,
  icon,
  active,
  onClick
}) => (
  <button
    type="button"
    onClick={onClick}
    className={`flex-1 p-4 border-2 rounded-lg font-semibold transition-all duration-200 flex items-center justify-center ${
      active
        ? 'border-blue-500 bg-blue-50 text-blue-700'
        : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
    }`}
  >
    <span className="mr-2 text-xl">{icon}</span>
    {label}
  </button>
);
