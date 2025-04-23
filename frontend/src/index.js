/**
 * This is the main entry point for the React application.
 * It renders the root component (App) into the DOM.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';


// Create a root element to render the React app
const root = ReactDOM.createRoot(document.getElementById('root'));

// Render the App component to the DOM
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

