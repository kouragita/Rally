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
