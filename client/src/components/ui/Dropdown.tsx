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
