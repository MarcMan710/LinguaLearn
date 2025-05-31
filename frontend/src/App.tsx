import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import Navigation from './components/Navigation';
import Home from './components/Home';
import Courses from './components/Courses';
import Profile from './components/Profile';
import NotificationCenter from './components/notifications/NotificationCenter';
import AccessibilitySettings from './components/accessibility/AccessibilitySettings';
import './styles/accessibility.css';

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <Router>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
          <a href="#main-content" className="skip-link sr-only focus:not-sr-only">
            Skip to main content
          </a>
          
          <Navigation />
          
          <main id="main-content" className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/courses" element={<Courses />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/notifications" element={<NotificationCenter />} />
              <Route path="/accessibility" element={<AccessibilitySettings />} />
            </Routes>
          </main>
          
          <footer className="bg-white dark:bg-gray-800 shadow-lg mt-8">
            <div className="container mx-auto px-4 py-6">
              <div className="flex justify-between items-center">
                <p className="text-gray-600 dark:text-gray-300">
                  © 2024 LinguaLearn. All rights reserved.
                </p>
                <a
                  href="/accessibility"
                  className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  Accessibility Settings
                </a>
              </div>
            </div>
          </footer>
        </div>
      </Router>
    </ThemeProvider>
  );
};

export default App;
