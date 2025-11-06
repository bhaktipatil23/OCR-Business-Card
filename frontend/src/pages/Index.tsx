import { useState } from "react";
import Navbar from "@/components/layout/Navbar";
import HeroSection from "@/components/uploads/HeroSection.tsx";
import FileTable from "@/components/table/FileTable";
import { FileData, ExtractedData } from "@/components/table/TableRow";
import DocumentPreviewModal from "@/components/PDFPreviewModal";
import { toast } from "sonner";
import { apiService } from "@/services/api";

const Index = () => {
  const [files, setFiles] = useState<FileData[]>([]);
  const [currentBatchId, setCurrentBatchId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [previewModal, setPreviewModal] = useState<{ isOpen: boolean; fileId: string; extractedData?: ExtractedData[]; filename?: string }>({ isOpen: false, fileId: '' });

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFiles = Array.from(event.target.files || []);
    await processUploadedFiles(uploadedFiles);
  };

  const processUploadedFiles = async (uploadedFiles: File[]) => {

    // Validation: Max 300 files
    if (uploadedFiles.length > 300) {
      toast.error("Maximum 300 files allowed", {
        description: "Please select fewer files and try again.",
      });
      return;
    }

    // Validation: File types (images and PDFs)
    const allowedExtensions = [".png", ".jpg", ".jpeg", ".pdf"];
    const invalidFiles = uploadedFiles.filter((file) => {
      const extension = "." + file.name.split(".").pop()?.toLowerCase();
      return !allowedExtensions.includes(extension);
    });

    if (invalidFiles.length > 0) {
      toast.error("Invalid file types detected", {
        description: "Only image files (PNG, JPG, JPEG) and PDF files are allowed.",
      });
      return;
    }

    // Validation: Total batch size (20MB limit)
    const maxBatchSizeBytes = 20 * 1024 * 1024; // 20MB in bytes
    const totalSize = uploadedFiles.reduce((sum, file) => sum + file.size, 0);

    if (totalSize > maxBatchSizeBytes) {
      const totalSizeMB = (totalSize / (1024 * 1024)).toFixed(1);
      toast.error("Batch too large", {
        description: `Total size ${totalSizeMB}MB exceeds 20MB limit. Please select fewer or smaller files.`,
      });
      return;
    }

    try {
      setIsUploading(true);
      
      // Upload files to backend
      const uploadResponse = await apiService.uploadFiles(uploadedFiles);
      setCurrentBatchId(uploadResponse.batch_id);
      
      // Process files for display
      const processedFiles: FileData[] = uploadResponse.uploaded_files.map((file, index) => {
        const originalFile = uploadedFiles[index];
        const webkitPath = (originalFile as any).webkitRelativePath;
        
        return {
          id: file.file_id,
          name: file.filename,
          size: file.size,
          type: originalFile?.type || 'application/octet-stream',
          path: file.file_path,
          status: "uploaded",
          uploadedAt: new Date(),
          parent: webkitPath ? webkitPath.split("/")[0] : "Direct Upload",
        };
      });

      setFiles(processedFiles);
      toast.success(`${processedFiles.length} file${processedFiles.length > 1 ? 's' : ''} uploaded successfully`, {
        description: "Starting validation...",
      });
      
      // Start validation automatically
      await handleValidateFiles(uploadResponse.batch_id);
      
    } catch (error) {
      toast.error("Upload failed", {
        description: error instanceof Error ? error.message : "Unknown error occurred",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleValidateFiles = async (batchId: string) => {
    try {
      // Update file status to validating
      setFiles(prev => prev.map(file => ({ ...file, status: "validating" })));
      
      const validationResponse = await apiService.validateFiles(batchId);
      
      // Get detailed validation results
      const validationStatus = await apiService.getValidationStatus(batchId);
      
      // Update files with validation results
      setFiles(prev => prev.map(file => {
        // Find validation result for this file
        let validationResult = null;
        let isValid = false;
        
        // Check in valid business cards
        const validCard = validationStatus.valid_business_cards?.find((card: any) => card.file_id === file.id);
        if (validCard) {
          validationResult = validCard.validation;
          isValid = true;
        } else {
          // Check in invalid files
          const invalidFile = validationStatus.invalid_files?.find((invalid: any) => invalid.file_id === file.id);
          if (invalidFile) {
            validationResult = invalidFile.validation;
            isValid = false;
          }
        }
        
        return {
          ...file,
          status: isValid ? "valid" : "invalid",
          validation: validationResult
        };
      }));
      
      if (validationResponse.valid_business_cards > 0) {
        toast.success(`Validation completed!`, {
          description: `${validationResponse.valid_business_cards} business cards found, ${validationResponse.invalid_files} invalid files. Starting processing...`,
        });
        
        // Start processing automatically for valid files
        await handleProcessFiles(batchId);
      } else {
        toast.error("No business cards found", {
          description: "Please upload valid business card images.",
        });
      }
      
    } catch (error) {
      toast.error("Validation failed", {
        description: error instanceof Error ? error.message : "Unknown error occurred",
      });
      setFiles(prev => prev.map(file => ({ ...file, status: "error" })));
    }
  };

  const handleProcessFiles = async (batchId: string) => {
    try {
      await apiService.processFiles(batchId);
      
      // Update file status to processing (only for valid files)
      setFiles(prev => prev.map(file => ({
        ...file,
        status: file.status === "valid" ? "processing" : file.status
      })));
      
      toast.success("Processing started", {
        description: "Valid business cards are being processed. You can download the results when complete.",
      });
      
      // Poll for status updates
      pollProcessingStatus(batchId);
      
    } catch (error) {
      toast.error("Processing failed", {
        description: error instanceof Error ? error.message : "Unknown error occurred",
      });
    }
  };

  const pollProcessingStatus = async (batchId: string) => {
    let isCompleted = false;
    const pollInterval = setInterval(async () => {
      if (isCompleted) {
        clearInterval(pollInterval);
        return;
      }
      
      try {
        const status = await apiService.getStatus(batchId);
        
        if (status.status === "completed") {
          isCompleted = true;
          
          // Final fetch of extracted data
          try {
            const extractedDataResponse = await apiService.getExtractedData(batchId);
            setFiles(prev => prev.map(file => {
              const extractedFile = extractedDataResponse.find(ed => ed.file_id === file.id);
              return {
                ...file,
                status: file.status === "processing" ? "completed" : file.status,
                extractedData: extractedFile?.extracted_data || []
              };
            }));
          } catch (extractError) {
            setFiles(prev => prev.map(file => ({
              ...file,
              status: file.status === "processing" ? "completed" : file.status
            })));
          }
          
          toast.success("Processing completed!", {
            description: "Your files have been processed successfully.",
          });
          clearInterval(pollInterval);
        } else if (status.status === "failed") {
          isCompleted = true;
          setFiles(prev => prev.map(file => ({
            ...file,
            status: file.status === "processing" ? "error" : file.status
          })));
          toast.error("Processing failed", {
            description: "An error occurred during processing.",
          });
          clearInterval(pollInterval);
        }
      } catch (error) {
        console.error("Status polling error:", error);
        clearInterval(pollInterval);
      }
    }, 2000); // Poll every 2 seconds
  };

  const handleDownload = () => {
    if (currentBatchId) {
      const downloadUrl = apiService.getDownloadUrl(currentBatchId);
      window.open(downloadUrl, '_blank');
    }
  };

  const handleVCFDownload = () => {
    if (currentBatchId) {
      const hostname = window.location.hostname;
      const baseUrl = hostname === 'localhost' || hostname === '127.0.0.1' 
        ? 'http://localhost:8000' 
        : `http://${hostname}:8000`;
      const vcfUrl = `${baseUrl}/api/v1/export-vcf/${currentBatchId}`;
      window.open(vcfUrl, '_blank');
    }
  };

  const handleFileClick = (fileId: string) => {
    const file = files.find(f => f.id === fileId);
    setPreviewModal({ 
      isOpen: true, 
      fileId,
      extractedData: file?.extractedData,
      filename: file?.name
    });
  };

  const closePreviewModal = () => {
    setPreviewModal({ isOpen: false, fileId: '', extractedData: undefined, filename: undefined });
  };

  return (
    <div className="h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col justify-center">
        <HeroSection 
          onUpload={handleFileUpload} 
          isUploading={isUploading} 
        />
        {files.length > 0 && (
          <div className="space-y-4">
            <FileTable files={files} onFileClick={handleFileClick} />
            {currentBatchId && files.some(f => f.status === "completed" && f.validation?.is_business_card !== false) && (
              <div className="flex justify-center gap-4">
                <button
                  onClick={handleDownload}
                  className="px-6 py-3 bg-navy-primary text-white rounded-lg hover:bg-navy-primary/80 transition-all duration-300 hover:opacity-80 hover:scale-105"
                >
                  Download CSV
                </button>
                <button
                  onClick={handleVCFDownload}
                  className="px-6 py-3 bg-navy-primary text-white rounded-lg hover:bg-navy-primary/80 transition-all duration-300 hover:opacity-80 hover:scale-105"
                >
                  Download VCF
                </button>
              </div>
            )}
          </div>
        )}
        
        <DocumentPreviewModal
          isOpen={previewModal.isOpen}
          onClose={closePreviewModal}
          fileId={previewModal.fileId}
          extractedData={previewModal.extractedData}
          filename={previewModal.filename}
        />
      </main>
    </div>
  );
};

export default Index;
