import React, { useState } from 'react';
import LoadingSpinner from './LoadingSpinner';
import { generateImage, saveImage } from '../services/mock-api';

const ImageGenerator = () => {
  const [prompt, setPrompt] = useState('');
  const [generatedImage, setGeneratedImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePromptChange = (e) => {
    setPrompt(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      setError('Please enter a text description');
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      // Use the generate api
      const data = await await generateImage({ prompt });;
      setGeneratedImage(data.image);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = () => {
    if (!generatedImage) return;
    
    // Create a temporary anchor element and trigger download
    const a = document.createElement('a');
    a.href = generatedImage;
    a.download = `generated-image-${Date.now()}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const handleSave = async () => {
    if (!generatedImage) return;
    
    try {
      //Use the save image api
      await saveImage(generatedImage, prompt);
      alert('Image saved to gallery');
    } catch (error) {
      console.error('Failed to save image:', error);
      alert('Failed to save image');
    }
  };

  return (
    <div className="image-generator">
      <div className="container">
        <form onSubmit={handleSubmit} className="generator-form">
          <div className="form-group">
            <label htmlFor="prompt">Text Description</label>
            <textarea
              id="prompt"
              value={prompt}
              onChange={handlePromptChange}
              placeholder="Describe the image you want to generate, e.g., 'A fox under moonlight'"
              rows={4}
              required
            />
          </div>

          <button type="submit" className="generate-btn" disabled={isLoading}>
            Generate Image
          </button>
        </form>

        <div className="result-container">
          {isLoading ? (
            <LoadingSpinner />
          ) : error ? (
            <div className="error-message">{error}</div>
          ) : generatedImage ? (
            <div className="generated-image-container">
              <img 
                src={generatedImage} 
                alt="Generated image" 
                className="generated-image" 
              />
              <div className="image-actions">
                <button onClick={handleSave} className="save-btn">
                  Save to Gallery
                </button>
                <button onClick={handleDownload} className="download-btn">
                  Download Image
                </button>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default ImageGenerator;