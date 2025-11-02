import { useState, useEffect } from "react";

type RobustImageProps = {
  images: string | string[];
  alt: string;
  className?: string;
  fallback: React.ReactNode;
  randomCount?: number; // how many random images to generate if none are found
};

const generateRandomImages = (count: number = 5): string[] => {
  const usedNumbers = new Set<number>();
  const urls: string[] = [];

  while (urls.length < count) {
    const rand = Math.floor(Math.random() * 10000) + 1; // random number up to 10k
    if (!usedNumbers.has(rand)) {
      usedNumbers.add(rand);
      urls.push(`https://picsum.photos/400/300?random=${rand}`);
    }
  }

  return urls;
};

const RobustImageComponent: React.FC<RobustImageProps> = ({
  images,
  alt,
  className,
  fallback,
  randomCount = 5,
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [hasError, setHasError] = useState(false);
  const [randomImage, setRandomImage] = useState<string | null>(null);

  const imageArray = Array.isArray(images) ? images : [images];

  const validImages = imageArray.filter(
    (img) =>
      img &&
      typeof img === "string" &&
      img.trim() !== "" &&
      !img.toLowerCase().includes("placeholder") &&
      !img.toLowerCase().includes("signup")
  );

  const handleError = () => {
    if (currentIndex < validImages.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      setHasError(true);
    }
  };

  useEffect(() => {
    setCurrentIndex(0);
    setHasError(false);

    if (!validImages.length) {
      // Dynamically generate random URLs — no repeats
      const randomUrls = generateRandomImages(randomCount);
      const chosen = randomUrls[Math.floor(Math.random() * randomUrls.length)];
      setRandomImage(chosen);
    } else {
      setRandomImage(null);
    }
  }, [images, randomCount]);

  if (hasError && !randomImage) {
    return <>{fallback}</>;
  }

  const imageSrc = validImages.length ? validImages[currentIndex] : randomImage;

  return (
    <img
      src={imageSrc || ""}
      alt={alt}
      className={className}
      onError={handleError}
    />
  );
};

export default RobustImageComponent;
