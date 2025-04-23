import React, { useState, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner';

// this is for frontend test:
// import { getSavedImages, deleteImage } from '../services/mock-api';
// import real api when backend is ready
import { getSavedImages, deleteImage } from '../services/api';

const Gallery = () => {
  const [images, setImages] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchImages = async () => {
    try {
      // Get saved images
      const data = await getSavedImages();
      console.log("Fetched images:", data);
      setImages(data.images);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchImages();
  }, []);

  const handleDownload = (imageUrl, prompt) => {
    // Create a temporary anchor element and trigger download
    const a = document.createElement('a');
    a.href = imageUrl;
    a.download = `${prompt.slice(0, 20).replace(/\s+/g, '-')}-${Date.now()}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

   // Handle image deletion
   const handleDelete = async (imageId) => {
    if (window.confirm('Are you sure you want to delete this image?')) {
      try {
        await deleteImage(imageId);
        // Refresh the image list after deletion
        fetchImages();
        // Show success message
        alert('Image deleted successfully');
      } catch (error) {
        console.error('Failed to delete image:', error);
        alert('Failed to delete image: ' + error.message);
      }
    }
  };

  if (isLoading) {
    return <div className="gallery container"><LoadingSpinner /></div>;
  }

  if (error) {
    return <div className="gallery container"><div className="error-message">{error}</div></div>;
  }

  const IMAGE_BASE_URL = "http://localhost:5000"
  return (
    <div className="gallery">
      <div className="container">
        <h2>Saved Images</h2>
        
        {images.length === 0 ? (
          <p className="no-images">No saved images yet</p>
        ) : (
          <div className="gallery-grid">
            {images.map((image) => (
                <div key={image.id} className="gallery-item">
                  <img src={`${IMAGE_BASE_URL}${image.url}`} alt={image.prompt}/>
                  <div className="gallery-item-details">
                    <p>{image.prompt}</p>
                    <span>{new Date(image.createdAt).toLocaleString()}</span>
                    <div>
                      <button
                          className="download-btn-sm"
                          onClick={() => handleDownload(image.url, image.prompt)}
                      >
                        Download
                      </button>
                      <button 
                        className="delete-btn-sm"
                        onClick={() => handleDelete(image.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Gallery;