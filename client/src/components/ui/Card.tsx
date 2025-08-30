import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  hover = false
}) => {
  return (
    <div
      className={`card ${hover ? 'hover:shadow-lg hover:-translate-y-1' : ''} ${className}`}
    >
      {children}
    </div>
  );
};

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  icon?: string;
}

export const CardHeader: React.FC<CardHeaderProps> = ({
  title,
  subtitle,
  icon
}) => {
  return (
    <div className="bg-gradient-to-r from-blue-50 to-green-50 px-6 py-4 border-b">
      <h2 className="text-2xl font-semibold text-gray-800 flex items-center">
        {icon && (
          <span className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center mr-3 text-white">
            {icon}
          </span>
        )}
        {title}
      </h2>
      {subtitle && (
        <p className="text-gray-600 mt-1">{subtitle}</p>
      )}
    </div>
  );
};

export const CardBody: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = ''
}) => {
  return (
    <div className={`p-6 ${className}`}>
      {children}
    </div>
  );
};
