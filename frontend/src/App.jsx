import React, { useState } from 'react';
import Header from './components/Header';
import ImageGenerator from './components/ImageGenerator';
import Gallery from './components/Gallery';
import Footer from './components/Footer';
import './styles.css';

const App = () => {
  const [activeTab, setActiveTab] = useState('generator');

  return (
    <div className="app">
      <Header />
      
      <nav className="main-nav">
        <div className="container">
          <button
            className={`nav-tab ${activeTab === 'generator' ? 'active' : ''}`}
            onClick={() => setActiveTab('generator')}
          >
            Image Generator
          </button>
          <button
            className={`nav-tab ${activeTab === 'gallery' ? 'active' : ''}`}
            onClick={() => setActiveTab('gallery')}
          >
            Gallery
          </button>
        </div>
      </nav>
      
      <main>
        {activeTab === 'generator' ? <ImageGenerator /> : <Gallery />}
      </main>
      
      <Footer />
    </div>
  );
};

export default App;