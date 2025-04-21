/**
 * This file encapsulates all interactions with the backend API
 * 
 * 
 * POST /api/generate:
Input: { "prompt": "Text description" }
Output: { "image": "imageUrl" }

GET /api/images:
Output: { "images": [{ "id": "savedImageId", "url": "imageUrl", "prompt": "textDescription", "createdAt": "timestamp" }] }

POST /api/images:
Input: { "image": "imageUrl", "prompt": "textDescription" }
Output: { "success": true, "id": "savedImageId" }
 * 
 */

// Base URL for the backend API
const API_BASE_URL = 'http://localhost:5000/api';

/**
 * API call to generate an image
 * @param {Object} params - Generation parameters
 * @param {string} params.prompt - Text description
 * @returns {Promise<Object>} - Response containing the generated image URL
 */
export const generateImage = async (params) => {
  try {
    const response = await fetch(`${API_BASE_URL}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Image generation failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Error generating image:', error);
    throw error;
  }
};

/**
 * Get saved images
 * @returns {Promise<Object>} - Response containing the list of images
 */
export const getSavedImages = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/images`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to fetch images');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching saved images:', error);
    throw error;
  }
};

/**
 * Save image to gallery
 * @param {string} imageUrl - Image URL
 * @param {string} prompt - Text description used to generate the image
 * @returns {Promise<Object>} - Save result
 */
export const saveImage = async (imageUrl, prompt) => {
  try {
    const response = await fetch(`${API_BASE_URL}/images`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image: imageUrl,
        prompt
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to save image');
    }

    return await response.json();
  } catch (error) {
    console.error('Error saving image:', error);
    throw error;
  }
};

// Export all API functions
export default {
  generateImage,
  getSavedImages,
  saveImage
};