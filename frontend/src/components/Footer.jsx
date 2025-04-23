import React from 'react';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="container">
        <p>© {new Date().getFullYear()} Text-to-Image Generation App | Powered by Stable Diffusion</p>
        <p> Developed by: Jiang Han | Snehal Shivaji Molavade | Tingyi Ruan </p>
      </div>
    </footer>
  );
};

export default Footer;