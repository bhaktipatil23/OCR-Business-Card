import { Upload, FolderOpen, FileImage } from "lucide-react";
import { useRef, useState } from "react";

interface DragDropUploadProps {
  onUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
  isUploading?: boolean;
  uploadType: 'folder' | 'files';
  onUploadTypeChange: (type: 'folder' | 'files') => void;
}

const DragDropUpload = ({ onUpload, isUploading = false, uploadType, onUploadTypeChange }: DragDropUploadProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const folderInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleClick = () => {
    if (uploadType === 'folder') {
      folderInputRef.current?.click();
    } else {
      fileInputRef.current?.click();
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const targetInput = uploadType === 'folder' ? folderInputRef.current : fileInputRef.current;
      if (targetInput) {
        const dataTransfer = new DataTransfer();
        Array.from(files).forEach(file => dataTransfer.items.add(file));
        targetInput.files = dataTransfer.files;
        
        const event = new Event('change', { bubbles: true });
        targetInput.dispatchEvent(event);
      }
    }
  };

  const getUploadText = () => {
    if (isDragging) {
      return uploadType === 'folder' ? 'Drop your folder here' : 'Drop your files here';
    }
    return uploadType === 'folder' ? 'Upload Document Folder' : 'Upload Files';
  };

  const getDescriptionText = () => {
    return uploadType === 'folder' 
      ? 'Drag and drop your folder with images or PDFs here, or click to browse'
      : 'Drag and drop your images (PNG, JPG, JPEG) or PDF files here, or click to browse';
  };

  const getButtonText = () => {
    if (isUploading) return 'Uploading...';
    return uploadType === 'folder' ? 'Choose Folder' : 'Choose Files';
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-3 sm:space-y-4 px-2 phone-full-width">
      {/* Upload Type Toggle */}
      <div className="flex justify-center px-2">
        <div className="bg-white rounded-xl p-1 shadow-md w-full sm:w-auto max-w-sm phone-full-width">
          <button
            onClick={() => onUploadTypeChange('folder')}
            className={`w-1/2 sm:w-auto px-3 py-2 rounded-lg font-medium transition-all duration-300 text-sm sm:text-base touch-target ${
              uploadType === 'folder'
                ? 'bg-navy-primary text-white shadow-md'
                : 'text-navy-primary hover:bg-gray-100'
            }`}
          >
            <FolderOpen className="w-4 h-4 inline mr-1" />
            <span className="phone-small-text">Folder</span>
          </button>
          <button
            onClick={() => onUploadTypeChange('files')}
            className={`w-1/2 sm:w-auto px-3 py-2 rounded-lg font-medium transition-all duration-300 text-sm sm:text-base touch-target ${
              uploadType === 'files'
                ? 'bg-navy-primary text-white shadow-md'
                : 'text-navy-primary hover:bg-gray-100'
            }`}
          >
            <FileImage className="w-4 h-4 inline mr-1" />
            <span className="phone-small-text">Files</span>
          </button>
        </div>
      </div>

      {/* Upload Area */}
      <div
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          relative cursor-pointer bg-gradient-to-r from-navy-primary to-blue-accent 
          rounded-xl sm:rounded-3xl p-4 sm:p-6 
          border-2 border-dashed transition-all duration-300 
          hover:shadow-2xl group shadow-md phone-full-width
          ${isDragging
            ? 'border-white bg-gradient-to-r from-navy-primary to-blue-accent shadow-2xl' 
            : 'border-white hover:border-white'
          }
        `}
      >
        <div className="flex flex-col items-center justify-center text-center space-y-3 sm:space-y-4">
          <div className={`
            w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl bg-white 
            flex items-center justify-center shadow-xl transition-transform duration-300
            ${isDragging ? 'scale-110 rotate-6' : 'group-hover:scale-110'}
          `}>
            {isDragging ? (
              uploadType === 'folder' ? (
                <FolderOpen className="w-5 h-5 sm:w-6 sm:h-6 text-navy-primary" />
              ) : (
                <FileImage className="w-5 h-5 sm:w-6 sm:h-6 text-navy-primary" />
              )
            ) : (
              <Upload className="w-5 h-5 sm:w-6 sm:h-6 text-navy-primary" />
            )}
          </div>
          
          <div className="space-y-1 sm:space-y-2">
            <h3 className="text-base sm:text-lg font-bold text-white phone-small-text">
              {getUploadText()}
            </h3>
            <p className="text-sm sm:text-base text-white/80 px-2 phone-small-text leading-tight">
              {getDescriptionText()}
            </p>
          </div>
          
          <button 
            disabled={isUploading}
            className="w-full sm:w-auto px-6 sm:px-8 py-2.5 sm:py-3 bg-white text-navy-primary rounded-lg sm:rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base min-h-[44px] touch-target"
          >
            {getButtonText()}
          </button>
        </div>
      </div>
      
      {/* Folder Input */}
      <input
        ref={folderInputRef}
        type="file"
        // @ts-ignore - webkitdirectory is not in TypeScript types
        webkitdirectory=""
        mozdirectory=""
        directory=""
        multiple
        onChange={onUpload}
        className="hidden"
      />
      
      {/* File Input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".png,.jpg,.jpeg,.pdf"
        onChange={onUpload}
        className="hidden"
      />

    </div>
  );
};

export default DragDropUpload;
