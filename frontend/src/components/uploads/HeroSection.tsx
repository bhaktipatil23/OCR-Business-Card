import { useState } from "react";
import DragDropUpload from "./DragDropUpload";
import InfoSection from "./InfoSection";

interface HeroSectionProps {
  onUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
  isUploading?: boolean;
}

const HeroSection = ({ onUpload, isUploading = false }: HeroSectionProps) => {
  const [uploadType, setUploadType] = useState<'folder' | 'files'>('folder');

  return (
    <div className="flex flex-col items-center text-center space-y-4 sm:space-y-6 px-2 sm:px-4 phone-container">
      <div className="space-y-2 sm:space-y-4 max-w-3xl w-full phone-full-width">
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-navy-primary via-blue-accent to-navy-primary bg-clip-text text-transparent">
          ReCircle Card AI
        </h1>
        <p className="text-base sm:text-lg text-muted-foreground px-2">
          Transform Your Documents with Intelligent Processing
        </p>
      </div>
      
      <DragDropUpload 
        onUpload={onUpload}
        isUploading={isUploading} 
        uploadType={uploadType}
        onUploadTypeChange={setUploadType}
      />
      
      <InfoSection />
    </div>
  );
};

export default HeroSection;
