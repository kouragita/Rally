import { ChartData } from '../services/types';

export const formatTemperature = (temp: number): string => {
  return temp > 0 ? `+${temp}°C` : `${temp}°C`;
};

export const formatPercentage = (value: number): string => {
  return value > 0 ? `+${value}%` : `${value}%`;
};

export const formatLargeNumber = (num: number): string => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toString();
};

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

export const generateMockChartData = (points: number = 5): ChartData[] => {
  return Array.from({ length: points }, (_, i) => ({
    name: `${2020 + i}`,
    value: Math.round((Math.random() * 3 + 0.5) * 100) / 100,
  }));
};
