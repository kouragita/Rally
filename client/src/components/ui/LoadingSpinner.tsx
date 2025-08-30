import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
  subMessage?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  message = 'Loading...',
  subMessage
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-16 h-16',
    lg: 'w-24 h-24'
  };

  return (
    <div className="flex flex-col items-center justify-center py-12 animate-fade-in">
      <div className={`relative ${sizeClasses[size]} mb-4`}>
        <div className="absolute inset-0 border-4 border-blue-200 rounded-full"></div>
        <div className="absolute inset-0 border-4 border-blue-500 rounded-full animate-spin border-t-transparent"></div>
      </div>
      
      {message && (
        <p className="text-lg font-semibold text-gray-700 mb-1">{message}</p>
      )}
      
      {subMessage && (
        <p className="text-sm text-gray-500 text-center max-w-md">{subMessage}</p>
      )}
    </div>
  );
};
