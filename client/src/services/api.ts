import axios from 'axios';
import { AnalysisQuery, AnalysisResult } from './types';

const API_BASE_URL = '/api/v1';

export class ApiService {
  static async getEcosystems() {
    const response = await axios.get(`${API_BASE_URL}/ecosystems/`);
    return response.data;
  }

  static async getSpecies() {
    const response = await axios.get(`${API_BASE_URL}/species/`);
    return response.data;
  }

  static async triggerAnalysis(payload: AnalysisQuery): Promise<{ report_id: number; message: string }> {
    const response = await axios.post(`${API_BASE_URL}/analysis/`, payload);
    return response.data; // Returns { report_id: number, message: string }
  }

  static async getReport(reportId: number): Promise<AnalysisResult> {
    const response = await axios.get(`${API_BASE_URL}/reports/${reportId}`);
    return response.data; // Returns the full report object
  }

  // Add a placeholder for getRecentAnalyses if needed later
  static async getRecentAnalyses(): Promise<AnalysisResult[]> {
    // This endpoint doesn't exist yet in our backend, so we'll return mock data for now
    return []; 
  }
}
