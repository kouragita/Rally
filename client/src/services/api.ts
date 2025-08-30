import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'; // Our FastAPI backend

export const getEcosystems = async () => {
  const response = await axios.get(`${API_BASE_URL}/ecosystems/`);
  return response.data;
};

export const getSpecies = async () => {
  const response = await axios.get(`${API_BASE_URL}/species/`);
  return response.data;
};

export const triggerAnalysis = async (payload: { query: string; target_type: string; target_name: string; target_id?: number }) => {
  const response = await axios.post(`${API_BASE_URL}/analysis/`, payload);
  return response.data; // Returns { report_id: number, message: string }
};

export const getReport = async (reportId: number) => {
  const response = await axios.get(`${API_BASE_URL}/reports/${reportId}`);
  return response.data; // Returns the full report object
};
