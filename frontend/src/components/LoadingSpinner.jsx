import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="loading-container">
      <div className="loading-spinner"></div>
      <p>Generating, please wait...</p>
    </div>
  );
};

export default LoadingSpinner;
