
/**
 * Mock API service for testing the frontend without a backend
 * This file simulates API responses that would normally come from the server
 */

// Sample image URLs (placeholder images)
const PLACEHOLDER_IMAGES = [
    '/test-img/img4.jpg',
    '/test-img/img5.jpg'
  ];
  
  // In-memory storage for saved images
  let savedImages = [
    {
      id: '1',
      url: '/test-img/img1.jpg',
      prompt: 'A beautiful sunset over mountains',
      createdAt: '2025-04-15T14:30:00Z'
    },
    {
      id: '2',
      url: '/test-img/img2.jpg',
      prompt: 'A futuristic city with flying cars',
      createdAt: '2025-04-16T10:15:00Z'
    },
    {
      id: '3',
      url: '/test-img/img3.jpg',
      prompt: 'An astronaut riding a horse',
      createdAt: '2025-04-17T09:45:00Z'
    }
  ];
  
  /**
   * Generates a random delay between min and max milliseconds
   * Used to simulate network latency
   */
  const randomDelay = (min = 500, max = 2000) => {
    const delay = Math.floor(Math.random() * (max - min + 1)) + min;
    return new Promise(resolve => setTimeout(resolve, delay));
  };
  
  /**
   * Simulates image generation API
   * @param {Object} params - Generation parameters
   * @param {string} params.prompt - Text description
   * @returns {Promise<Object>} - Response containing the generated image URL
   */
  export const generateImage = async (params) => {
    // Simulate network delay
    await randomDelay();
    
    // Randomly select a placeholder image
    const randomIndex = Math.floor(Math.random() * PLACEHOLDER_IMAGES.length);
    const imageUrl = PLACEHOLDER_IMAGES[randomIndex];
    
    // 10% chance of simulating an error
    if (Math.random() < 0.1) {
      throw new Error('Image generation failed. Please try again.');
    }
    
    return {
      image: imageUrl,
      prompt: params.prompt
    };
  };
  
  /**
   * Get saved images
   * @returns {Promise<Object>} - Response containing the list of images
   */
  export const getSavedImages = async () => {
    // Simulate network delay
    await randomDelay(300, 1000);
    
    // 5% chance of simulating an error
    if (Math.random() < 0.05) {
      throw new Error('Failed to fetch images. Please try again later.');
    }
    
    return {
      images: [...savedImages]
    };
  };
  
  /**
   * Save image to gallery
   * @param {string} imageUrl - Image URL
   * @param {string} prompt - Text description used to generate the image
   * @returns {Promise<Object>} - Save result
   */
  export const saveImage = async (imageUrl, prompt) => {
    // Simulate network delay
    await randomDelay(200, 800);
    
    // 5% chance of simulating an error
    if (Math.random() < 0.05) {
      throw new Error('Failed to save image. Please try again later.');
    }
    
    // Create a new image entry
    const newImage = {
      id: Date.now().toString(),
      url: imageUrl,
      prompt: prompt,
      createdAt: new Date().toISOString()
    };
    
    // Add to the saved images array
    savedImages = [newImage, ...savedImages];
    
    return {
      success: true,
      id: newImage.id
    };
  };
  
  // Export all mock API functions
  export default {
    generateImage,
    getSavedImages,
    saveImage
  };