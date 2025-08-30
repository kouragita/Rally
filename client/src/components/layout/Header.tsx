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
