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
