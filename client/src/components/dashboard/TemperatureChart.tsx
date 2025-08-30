import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ChartData } from '../../services/types';

interface TemperatureChartProps {
  data: ChartData[];
  title?: string;
}

export const TemperatureChart: React.FC<TemperatureChartProps> = ({
  data,
  title = "Temperature Change Over Time"
}) => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
        <span className="mr-2">🌡️</span>
        {title}
      </h3>
      
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="name" 
              stroke="#666"
              fontSize={12}
            />
            <YAxis 
              stroke="#666"
              fontSize={12}
              label={{ value: 'Temperature (°C)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
              }}
            />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="#ef4444" 
              strokeWidth={3}
              dot={{ fill: '#ef4444', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#ef4444', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
