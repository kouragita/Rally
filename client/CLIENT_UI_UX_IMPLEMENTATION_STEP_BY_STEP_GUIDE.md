# Climate & Wildlife AI Dashboard - Implementation Guide

## 🏗️ Project Structure Enhancement

Based on your current structure, here's how to organize your files for the enhanced UI:

```
src/
├── App.css
├── App.tsx
├── index.css
├── main.tsx
├── vite-env.d.ts
├── assets/
│   ├── react.svg
│   └── icons/              # New: Custom icons
├── components/             # New: React components
│   ├── ui/                 # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Dropdown.tsx
│   │   ├── Input.tsx
│   │   └── LoadingSpinner.tsx
│   ├── layout/             # Layout components
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── Layout.tsx
│   ├── forms/              # Form components
│   │   ├── AnalysisForm.tsx
│   │   └── QueryInput.tsx
│   ├── dashboard/          # Dashboard specific
│   │   ├── MetricCard.tsx
│   │   ├── ChartCard.tsx
│   │   └── ResultsPanel.tsx
│   └── charts/             # Data visualization
│       ├── TemperatureChart.tsx
│       └── PopulationChart.tsx
├── hooks/                  # New: Custom hooks
│   ├── useApi.ts
│   └── useLocalStorage.ts
├── services/
│   ├── api.ts             # Your existing API service
│   └── types.ts           # New: TypeScript types
├── styles/                # New: Additional styles
│   ├── globals.css
│   └── components.css
└── utils/                 # New: Utility functions
    ├── constants.ts
    └── helpers.ts
```

## 🎯 Step 1: Install Required Dependencies

First, install the necessary packages:

```bash
npm install lucide-react recharts tailwindcss @tailwindcss/forms
npm install -D @types/node
```

Initialize Tailwind CSS:

```bash
npx tailwindcss init -p
```

## 🎨 Step 2: Setup Design System

### Update `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#2D5A27',
          600: '#1e3a1e',
          700: '#163016',
        },
        accent: {
          500: '#4A90E2',
          600: '#3b82d6',
        },
        success: {
          500: '#7CB342',
          600: '#689f35',
        },
        warning: {
          500: '#FFC107',
          600: '#e0a806',
        },
        danger: {
          500: '#E74C3C',
          600: '#d43f2f',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
```

### Update `src/index.css`:

```css
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

@layer base {
  * {
    @apply border-border;
  }
  
  body {
    @apply bg-slate-50 text-slate-900;
    font-family: 'Inter', system-ui, sans-serif;
  }
}

@layer components {
  .btn-primary {
    @apply bg-gradient-to-r from-primary-500 to-accent-500 text-white px-6 py-3 rounded-lg font-semibold hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-200;
  }
  
  .btn-secondary {
    @apply bg-white border-2 border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:border-gray-400 transition-colors duration-200;
  }
  
  .card {
    @apply bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow duration-200;
  }
}
```

## 🧩 Step 3: Create Type Definitions

Create `src/services/types.ts`:

```typescript
export interface EcosystemOption {
  id: string;
  label: string;
  icon: string;
  description?: string;
}

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
```

## 🔧 Step 4: Create Utility Constants

Create `src/utils/constants.ts`:

```typescript
import { EcosystemOption, SpeciesOption } from '../services/types';

export const ECOSYSTEM_OPTIONS: EcosystemOption[] = [
  {
    id: 'arctic-terrestrial',
    label: 'Arctic Terrestrial Systems',
    icon: '🏔️',
    description: 'Tundra, permafrost, and cold-adapted ecosystems'
  },
  {
    id: 'tropical-rainforest',
    label: 'Tropical Rainforests',
    icon: '🌴',
    description: 'High biodiversity forest ecosystems'
  },
  {
    id: 'marine-coastal',
    label: 'Marine & Coastal',
    icon: '🌊',
    description: 'Ocean, coral reefs, and coastal environments'
  },
  {
    id: 'grasslands',
    label: 'Grasslands & Savannas',
    icon: '🌾',
    description: 'Open grassland and savanna ecosystems'
  },
  {
    id: 'freshwater',
    label: 'Freshwater Systems',
    icon: '🏞️',
    description: 'Rivers, lakes, and wetland environments'
  }
];

export const SPECIES_OPTIONS: SpeciesOption[] = [
  {
    id: 'polar-bear',
    label: 'Polar Bear',
    icon: '🐻‍❄️',
    ecosystemId: 'arctic-terrestrial',
    threatLevel: 'critical'
  },
  {
    id: 'arctic-fox',
    label: 'Arctic Fox',
    icon: '🦊',
    ecosystemId: 'arctic-terrestrial',
    threatLevel: 'high'
  },
  {
    id: 'jaguar',
    label: 'Jaguar',
    icon: '🐆',
    ecosystemId: 'tropical-rainforest',
    threatLevel: 'medium'
  },
  // Add more species as needed
];

export const THREAT_LEVEL_COLORS = {
  low: 'text-green-600 bg-green-50',
  medium: 'text-yellow-600 bg-yellow-50',
  high: 'text-orange-600 bg-orange-50',
  critical: 'text-red-600 bg-red-50'
};
```

## 🎨 Step 5: Create UI Components

### Create `src/components/ui/Card.tsx`:

```tsx
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
```

### Create `src/components/ui/Dropdown.tsx`:

```tsx
import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';

interface DropdownOption {
  id: string;
  label: string;
  icon?: string;
  description?: string;
}

interface DropdownProps {
  options: DropdownOption[];
  value?: string;
  onChange: (value: string) => void;
  placeholder: string;
  icon?: string;
  disabled?: boolean;
  className?: string;
}

export const Dropdown: React.FC<DropdownProps> = ({
  options,
  value,
  onChange,
  placeholder,
  icon,
  disabled = false,
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  const selectedOption = options.find(opt => opt.id === value);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (optionId: string) => {
    onChange(optionId);
    setIsOpen(false);
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        className={`w-full px-4 py-3 border-2 rounded-lg text-left flex items-center justify-between transition-all duration-200 ${
          disabled 
            ? 'bg-gray-100 border-gray-200 cursor-not-allowed text-gray-500' 
            : 'bg-white border-gray-200 hover:border-blue-400 focus:border-blue-500 focus:outline-none'
        }`}
        disabled={disabled}
      >
        <span className="flex items-center">
          {icon && <span className="mr-3 text-lg">{icon}</span>}
          <span className={selectedOption ? 'text-gray-800' : 'text-gray-500'}>
            {selectedOption?.label || placeholder}
          </span>
        </span>
        <ChevronDown 
          className={`w-5 h-5 transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          } ${disabled ? 'text-gray-400' : 'text-gray-600'}`} 
        />
      </button>

      {isOpen && !disabled && (
        <div className="absolute z-50 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto animate-slide-up">
          {options.map((option) => (
            <button
              key={option.id}
              onClick={() => handleSelect(option.id)}
              className="w-full px-4 py-3 text-left hover:bg-blue-50 flex items-center transition-colors duration-150 border-b border-gray-50 last:border-b-0"
            >
              <div className="flex items-center">
                {option.icon && <span className="mr-3 text-lg">{option.icon}</span>}
                <div>
                  <div className="font-medium text-gray-800">{option.label}</div>
                  {option.description && (
                    <div className="text-sm text-gray-500">{option.description}</div>
                  )}
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
```

### Create `src/components/ui/Input.tsx`:

```tsx
import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  icon?: string;
  error?: string;
  helperText?: string;
}

export const Input: React.FC<InputProps> = ({
  label,
  icon,
  error,
  helperText,
  className = '',
  ...props
}) => {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-semibold text-gray-700 flex items-center">
          {icon && <span className="mr-2">{icon}</span>}
          {label}
        </label>
      )}
      
      <div className="relative">
        <input
          className={`w-full px-4 py-3 border-2 rounded-lg transition-colors duration-200 focus:outline-none ${
            error 
              ? 'border-red-300 focus:border-red-500' 
              : 'border-gray-200 focus:border-blue-500'
          } ${className}`}
          {...props}
        />
        {props.type !== 'file' && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <span className="text-gray-400">💡</span>
          </div>
        )}
      </div>
      
      {error && (
        <p className="text-sm text-red-600 flex items-center">
          <span className="mr-1">⚠️</span>
          {error}
        </p>
      )}
      
      {helperText && !error && (
        <p className="text-xs text-gray-500">{helperText}</p>
      )}
    </div>
  );
};
```

### Create `src/components/ui/LoadingSpinner.tsx`:

```tsx
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
```

## 🏗️ Step 6: Create Layout Components

### Create `src/components/layout/Header.tsx`:

```tsx
import React from 'react';

export const Header: React.FC = () => {
  return (
    <header className="bg-gradient-to-r from-primary-500 to-accent-500 shadow-lg">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
              <span className="text-2xl">🌍</span>
            </div>
            <div>
              <h1 className="text-white text-xl font-bold">Climate & Wildlife AI</h1>
              <p className="text-green-100 text-sm">Environmental Intelligence Dashboard</p>
            </div>
          </div>
          
          <nav className="hidden md:flex space-x-6">
            <NavLink href="#dashboard">Dashboard</NavLink>
            <NavLink href="#analytics">Analytics</NavLink>
            <NavLink href="#reports">Reports</NavLink>
            <NavLink href="#settings">Settings</NavLink>
          </nav>
        </div>
      </div>
    </header>
  );
};

const NavLink: React.FC<{ href: string; children: React.ReactNode }> = ({ 
  href, 
  children 
}) => (
  <a 
    href={href}
    className="text-white hover:text-green-100 transition-colors duration-200 font-medium"
  >
    {children}
  </a>
);
```

### Create `src/components/layout/Layout.tsx`:

```tsx
import React from 'react';
import { Header } from './Header';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      <main className="container mx-auto px-6 py-8">
        {children}
      </main>
    </div>
  );
};
```

## 📝 Step 7: Create Form Components

### Create `src/components/forms/AnalysisForm.tsx`:

```tsx
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
```

## 🎯 Step 8: Update Your Main App Component

### Update `src/App.tsx`:

```tsx
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
```

## 🔄 Step 9: Update Your API Service

### Update `src/services/api.ts`:

```typescript
import { AnalysisQuery, AnalysisResult } from './types';

const API_BASE_URL = 'http://localhost:5000/api'; // Replace with your actual API URL

export class ApiService {
  static async submitAnalysis(query: AnalysisQuery): Promise<AnalysisResult> {
    try {
      const response = await fetch(`${API_BASE_URL}/analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(query),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('API call failed:', error);
      throw error;
    }
  }

  static async getRecentAnalyses(): Promise<AnalysisResult[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/analyses/recent`);
      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch recent analyses:', error);
      throw error;
    }
  }
}
```

## 🎨 Step 10: Create Dashboard Components (Optional Enhancement)

### Create `src/components/dashboard/MetricCard.tsx`:

```tsx
import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  color?: 'red' | 'blue' | 'green' | 'amber' | 'gray';
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  icon,
  trend,
  trendValue,
  color = 'blue',
  className = ''
}) => {
  const colorClasses = {
    red: 'bg-red-50 text-red-600 border-red-200',
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    amber: 'bg-amber-50 text-amber-600 border-amber-200',
    gray: 'bg-gray-50 text-gray-600 border-gray-200'
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-red-500" />;
      case 'down':
        return <TrendingDown className="w-4 h-4 text-green-500" />;
      case 'neutral':
        return <Minus className="w-4 h-4 text-gray-500" />;
      default:
        return null;
    }
  };

  return (
    <div className={`p-6 rounded-xl border-2 transition-all duration-200 hover:shadow-md ${colorClasses[color]} ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
        {trend && (
          <div className="flex items-center space-x-1">
            {getTrendIcon()}
            {trendValue && (
              <span className="text-sm font-medium">{trendValue}</span>
            )}
          </div>
        )}
      </div>
      
      <div className="text-3xl font-bold mb-1">{value}</div>
      <div className="text-sm font-medium opacity-80">{title}</div>
    </div>
  );
};
```

### Create `src/components/charts/TemperatureChart.tsx`:

```tsx
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
```

## 🚀 Step 11: Custom Hooks (Advanced)

### Create `src/hooks/useApi.ts`:

```typescript
import { useState, useCallback } from 'react';

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useApi<T>() {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(async (apiCall: () => Promise<T>) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const data = await apiCall();
      setState({ data, loading: false, error: null });
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred';
      setState({ data: null, loading: false, error: errorMessage });
      throw error;
    }
  }, []);

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}
```

## ⚡ Step 12: Performance Optimization

### Create `src/utils/helpers.ts`:

```typescript
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
```

## 🎯 Step 13: Final Integration Steps

### 1. Update your `package.json` scripts:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview",
    "type-check": "tsc --noEmit"
  }
}
```

### 2. Replace the App.tsx integration in your existing code:

You can now replace your current `App.tsx` with the enhanced version from Step 8, or integrate the components gradually.

### 3. Test the components:

```bash
npm run dev
```

## 🏁 Final Result

After implementing all these components, you'll have:

✅ **Modern, responsive UI** with nature-inspired design  
✅ **Interactive form components** with validation and feedback  
✅ **Loading states and animations** for better UX  
✅ **Modular component architecture** for easy maintenance  
✅ **TypeScript support** with proper type definitions  
✅ **Tailwind CSS** for consistent styling  
✅ **Data visualization ready** components  
✅ **Mobile-responsive design** that works on all devices  

## 🔄 Next Steps

1. **Implement the components gradually** - Start with the basic UI components
2. **Connect to your real API** - Replace the mock data with actual API calls
3. **Add data visualization** - Implement charts and graphs for your data
4. **Test on different devices** - Ensure mobile responsiveness
5. **Add more advanced features** - Filters, export functionality, etc.

Your dashboard will transform from the plain interface shown in your screenshot to a professional, engaging environmental intelligence platform! 🌍✨