export interface EcosystemOption {
  id: string;
  label: string;
  icon: string;
  description?: string;
}

// Added a comment to force re-compilation

export interface SpeciesOption {
  id: string;
  label: string;
  icon: string;
  ecosystemId: string;
  threatLevel: 'low' | 'medium' | 'high' | 'critical';
}

export interface AnalysisQuery {
  query: string;
  ecosystem?: string;
  species?: string;
  analysisType: 'ecosystem' | 'species';
}

export interface AnalysisResult {
  id: string;
  query: string;
  ecosystem: string;
  species?: string;
  metrics: {
    temperatureChange: number;
    precipitationChange: number;
    speciesAtRisk: number;
  };
  insights: string[];
  charts: {
    temperature: ChartData[];
    population: ChartData[];
  };
  timestamp: string;
}

export interface ChartData {
  name: string;
  value: number;
  date?: string;
}
