
import { useState, useEffect } from "react";


type RobustImageProps = {
  images: string | string[];
  alt: string;
  className?: string;
  fallback: React.ReactNode;
};

const RobustImageComponent: React.FC<RobustImageProps> = ({ images, alt, className, fallback }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [hasError, setHasError] = useState(false);
  
  // Convert to array if it's not already
  const imageArray = Array.isArray(images) ? images : [images];
  
  // Filter out invalid/empty URLs
  const validImages = imageArray.filter(img => img && typeof img === 'string' && img.trim() !== '');
  
  const handleError = () => {
    if (currentIndex < validImages.length - 1) {
      setCurrentIndex(prev => prev + 1);
    } else {
      setHasError(true);
    }
  };
  
  // Reset state when images change
  useEffect(() => {
    setCurrentIndex(0);
    setHasError(false);
  }, [images]);
  
  if (hasError || !validImages.length) {
    return <>{fallback}</>;
  }
  
  return (
    <img
      src={validImages[currentIndex]}
      alt={alt}
      className={className}
      onError={handleError}
    />
  );
};

export default RobustImageComponent; 