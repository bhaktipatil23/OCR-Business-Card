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
    <div className="w-full max-w-2xl mx-auto space-y-4">
      {/* Upload Type Toggle */}
      <div className="flex justify-center">
        <div className="bg-white rounded-xl p-1 shadow-md">
          <button
            onClick={() => onUploadTypeChange('folder')}
            className={`px-3 py-2 rounded-lg font-medium transition-all duration-300 ${
              uploadType === 'folder'
                ? 'bg-navy-primary text-white shadow-md'
                : 'text-navy-primary hover:bg-gray-100'
            }`}
          >
            <FolderOpen className="w-4 h-4 inline mr-1" />
            Folder
          </button>
          <button
            onClick={() => onUploadTypeChange('files')}
            className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 ${
              uploadType === 'files'
                ? 'bg-navy-primary text-white shadow-md'
                : 'text-navy-primary hover:bg-gray-100'
            }`}
          >
            <FileImage className="w-4 h-4 inline mr-2" />
            File Upload
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
          relative cursor-pointer bg-gradient-to-r from-navy-primary to-blue-accent rounded-3xl p-6 
          border-2 border-dashed transition-all duration-300 
          hover:shadow-2xl hover:scale-[1.02] group shadow-md
          ${isDragging
            ? 'border-white bg-gradient-to-r from-navy-primary to-blue-accent shadow-2xl scale-[1.02]' 
            : 'border-white hover:border-white'
          }
        `}
      >
        <div className="flex flex-col items-center justify-center text-center space-y-4">
          <div className={`
            w-12 h-12 rounded-2xl bg-white 
            flex items-center justify-center shadow-xl transition-transform duration-300
            ${isDragging ? 'scale-110 rotate-6' : 'group-hover:scale-110'}
          `}>
            {isDragging ? (
              uploadType === 'folder' ? (
                <FolderOpen className="w-6 h-6 text-navy-primary" />
              ) : (
                <FileImage className="w-6 h-6 text-navy-primary" />
              )
            ) : (
              <Upload className="w-6 h-6 text-navy-primary" />
            )}
          </div>
          
          <div className="space-y-2">
            <h3 className="text-lg font-bold text-white">
              {getUploadText()}
            </h3>
            <p className="text-white/80">
              {getDescriptionText()}
            </p>
          </div>
          
          <button 
            disabled={isUploading}
            className="px-8 py-3 bg-white text-navy-primary rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
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
