import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "@/components/layout/Navbar";
import HeroSection from "@/components/uploads/HeroSection.tsx";
import FileTable from "@/components/table/FileTable";
import DataTable from "@/components/table/DataTable";
import FormModal from "@/components/ui/FormModal";
import { FileData, ExtractedData } from "@/components/table/TableRow";
import DocumentPreviewModal from "@/components/PDFPreviewModal";

import { toast } from "sonner";
import { apiService } from "@/services/api";

const Index = () => {
  const navigate = useNavigate();
  const [files, setFiles] = useState<FileData[]>([]);
  const [currentBatchId, setCurrentBatchId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [previewModal, setPreviewModal] = useState<{ isOpen: boolean; fileId: string; extractedData?: ExtractedData[]; filename?: string }>({ isOpen: false, fileId: '' });
  const [allExtractedData, setAllExtractedData] = useState<ExtractedData[]>([]);
  const [saveModal, setSaveModal] = useState(false);
  const [emailModal, setEmailModal] = useState(false);
  const [formSubmissionCount, setFormSubmissionCount] = useState(0);
  const [savedFormData, setSavedFormData] = useState<{ name: string; team: string; event: string } | null>(null);
  const [isLoadingPersistentData, setIsLoadingPersistentData] = useState(false);
  
  const loadPersistentData = async () => {
    try {
      console.log('Starting to load persistent data...');
      setIsLoadingPersistentData(true);
      
      // Try to get recent batches
      const recentBatches = await apiService.getRecentBatches();
      console.log('Recent batches response:', recentBatches);
      
      if (recentBatches.batches && recentBatches.batches.length > 0) {
        const mostRecentBatch = recentBatches.batches[0];
        console.log('Most recent saved batch:', mostRecentBatch);
        
        // Try to load saved data from the latest batch
        try {
          const savedData = await apiService.getSavedData(mostRecentBatch.batch_id);
          console.log('Most recent saved data response:', savedData);
          
          if (savedData.extracted_data && savedData.extracted_data.length > 0) {
            setAllExtractedData(savedData.extracted_data);
            setCurrentBatchId(mostRecentBatch.batch_id);
            setSavedFormData({
              name: mostRecentBatch.name,
              team: mostRecentBatch.team,
              event: mostRecentBatch.event
            });
            setFormSubmissionCount(1);
            
            console.log('Successfully loaded most recent saved data');
            toast.success(`Loaded most recent saved data`, {
              description: `${savedData.total_records} records from ${mostRecentBatch.event}`,
            });
          } else {
            console.log('No extracted data found in saved data');
          }
        } catch (dataError) {
          console.error('Error loading saved data:', dataError);
        }
      } else {
        console.log('No recent batches found');
      }
    } catch (error) {
      console.error('Error loading recent batches:', error);
    } finally {
      setIsLoadingPersistentData(false);
    }
  };
  
  // Load persistent data on component mount
  useEffect(() => {
    loadPersistentData();
  }, []);


  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFiles = Array.from(event.target.files || []);
    await processUploadedFiles(uploadedFiles);
  };

  const processUploadedFiles = async (uploadedFiles: File[]) => {
    // Clear previous data when new files are uploaded
    setAllExtractedData([]);
    setCurrentBatchId(null);
    setSavedFormData(null);
    setFormSubmissionCount(0);

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
        description: "Starting UI simulation and queue processing...",
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
      // Set all files to pending initially
      setFiles(prev => prev.map(file => ({ ...file, status: "pending" })));
      
      // Start individual file validation and processing
      await processFilesIndividually(batchId);
      
    } catch (error) {
      toast.error("Processing failed", {
        description: error instanceof Error ? error.message : "Unknown error occurred",
      });
      setFiles(prev => prev.map(file => ({ ...file, status: "error" })));
    }
  };

  const processFilesIndividually = async (batchId: string) => {
    try {
      // Get batch validation results first
      const validationResponse = await apiService.validateFiles(batchId);
      const validationStatus = await apiService.getValidationStatus(batchId);
      
      // Start individual processing on backend
      await apiService.startIndividualProcessing(batchId);
      
      // Poll for individual file status updates
      pollIndividualFileStatus(batchId);
      
    } catch (error) {
      console.error('Individual processing error:', error);
      throw error;
    }
  };

  const pollIndividualFileStatus = async (batchId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const fileStatusResponse = await apiService.getFileStatus(batchId);
        
        // Update file statuses based on backend response
        setFiles(prev => prev.map(file => {
          const backendFileStatus = fileStatusResponse.files[file.id];
          if (backendFileStatus) {
            return {
              ...file,
              status: backendFileStatus.status as any,
              validation: backendFileStatus.validation,
              extractedData: backendFileStatus.extracted_data ? [backendFileStatus.extracted_data] : undefined
            };
          }
          return file;
        }));
        
        // Check if all files are processed
        const allProcessed = Object.values(fileStatusResponse.files).every(
          (fileStatus: any) => fileStatus.status === 'completed' || fileStatus.status === 'invalid'
        );
        
        if (allProcessed) {
          clearInterval(pollInterval);
          
          // Set all extracted data from queue
          setAllExtractedData(fileStatusResponse.queue_data || []);
          
          toast.success(`Queue processing completed!`, {
            description: `${fileStatusResponse.queue_data?.length || 0} records extracted and queued.`,
          });
        }
        
      } catch (error) {
        console.error('File status polling error:', error);
        clearInterval(pollInterval);
      }
    }, 1000); // Poll every second for real-time updates
  };

  const handleProcessFiles = async (batchId: string) => {
    // This method is no longer needed as individual processing handles everything
    console.log('Individual processing handles all queue logic');
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
          
          // Fetch all extracted data from queue at once
          try {
            const queueDataResponse = await apiService.getQueuedExtractedData(batchId);
            const allData: ExtractedData[] = queueDataResponse.extracted_data || [];
            
            // Update files status to completed
            setFiles(prev => prev.map(file => ({
              ...file,
              status: file.status === "processing" ? "completed" : file.status
            })));
            
            // Set all extracted data from queue
            setAllExtractedData(allData);
            
            toast.success(`Queue processed successfully!`, {
              description: `${allData.length} records extracted from ${queueDataResponse.total_records} files.`,
            });
          } catch (extractError) {
            console.error('Queue data fetch error:', extractError);
            setFiles(prev => prev.map(file => ({
              ...file,
              status: file.status === "processing" ? "completed" : file.status
            })));
            toast.error("Failed to fetch extracted data", {
              description: "Processing completed but data retrieval failed.",
            });
          }
          
          // Success message moved to queue data fetch section
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
    // Preview functionality disabled
  };

  const handleDataChange = (updatedData: ExtractedData[]) => {
    setAllExtractedData(updatedData);
  };

  const handleSave = async (data?: { name: string; team: string; event: string }) => {
    const formData = data || savedFormData;
    if (!formData) return;
    
    try {
      const hostname = window.location.hostname;
      const baseUrl = hostname === 'localhost' || hostname === '127.0.0.1' 
        ? 'http://localhost:8000' 
        : `http://${hostname}:8000`;
      
      const response = await fetch(`${baseUrl}/api/v1/save-data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.name,
          team: formData.team,
          event: formData.event,
          batch_id: currentBatchId || 'batch_' + Date.now(),
          extracted_data: allExtractedData
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        toast.success(`${result.message}`);
      } else {
        toast.error('Failed to save data');
      }
    } catch (error) {
      console.error('Save error:', error);
      toast.error('Error saving data');
    }
  };

  const handleExport = async (data?: { name: string; team: string; event: string }) => {
    const formData = data || savedFormData;
    if (!formData) return;
    
    // Save data first if needed
    await handleSave(formData);
    
    if (currentBatchId) {
      const downloadUrl = apiService.getDownloadUrl(currentBatchId);
      window.open(downloadUrl, '_blank');
    }
  };

  const handleSendEmail = async (data?: { name: string; team: string; event: string }) => {
    const formData = data || savedFormData;
    if (!formData) return;
    
    try {
      const hostname = window.location.hostname;
      const baseUrl = hostname === 'localhost' || hostname === '127.0.0.1' 
        ? 'http://localhost:8000' 
        : `http://${hostname}:8000`;
      
      const response = await fetch(`${baseUrl}/api/v1/save-email-data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.name,
          team: formData.team,
          event: formData.event,
          batch_id: currentBatchId || 'batch_' + Date.now(),
          extracted_data: allExtractedData
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        toast.success(`${result.message}`);
        
        navigate('/email', { 
          state: { 
            eventData: formData, 
            extractedData: allExtractedData 
          } 
        });
      } else {
        toast.error('Failed to save email data');
      }
    } catch (error) {
      console.error('Email save error:', error);
      toast.error('Error saving email data');
    }
  };

  const closePreviewModal = () => {
    setPreviewModal({ isOpen: false, fileId: '', extractedData: undefined, filename: undefined });
  };

  return (
    <div className="min-h-screen flex flex-col phone-full-width">
      <Navbar />
      <main className="flex-1 w-full mx-auto px-2 sm:px-6 lg:px-8 py-2 sm:py-4 phone-container">
        <div className={`${files.length > 0 || allExtractedData.length > 0 ? 'space-y-3 sm:space-y-6 phone-no-center' : 'flex flex-col justify-center min-h-[calc(100vh-80px)]'} phone-full-width`}>
          {isLoadingPersistentData && (
            <div className="text-center py-4">
              <div className="inline-flex items-center px-4 py-2 font-semibold leading-6 text-sm shadow rounded-md text-blue-500 bg-blue-100 transition ease-in-out duration-150">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Loading previous session data...
              </div>
            </div>
          )}
          
          {!isLoadingPersistentData && allExtractedData.length > 0 && files.length === 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-blue-800">
                    Previous session restored - {allExtractedData.length} business cards loaded from database
                  </p>
                </div>
              </div>
            </div>
          )}
          <HeroSection 
            onUpload={handleFileUpload} 
            isUploading={isUploading} 
          />
          {files.length > 0 && (
            <div className="space-y-3 sm:space-y-6 phone-full-width">
              <FileTable files={files} onFileClick={handleFileClick} />
            </div>
          )}
          
          {allExtractedData.length > 0 && (
            <div className="space-y-3 sm:space-y-6 phone-full-width">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-green-800">
                      {files.length > 0 ? 'Processing completed!' : 'Previous session data loaded'} - {allExtractedData.length} business cards extracted
                    </p>
                  </div>
                </div>
              </div>
              <DataTable data={allExtractedData} onDataChange={handleDataChange} />
              
              <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center px-2 phone-stack">
                <button
                  onClick={() => {
                    if (formSubmissionCount === 0) {
                      setSaveModal(true);
                    } else {
                      handleSave();
                    }
                  }}
                  className="w-full sm:w-auto px-4 sm:px-6 py-2.5 sm:py-3 text-sm sm:text-base bg-green-600 text-white rounded-lg hover:bg-green-700 transition-all duration-300 touch-target phone-full-width"
                >
                  Save
                </button>
                <button
                  onClick={() => {
                    if (formSubmissionCount === 0) {
                      setSaveModal(true);
                    } else {
                      handleExport();
                    }
                  }}
                  className="w-full sm:w-auto px-4 sm:px-6 py-2.5 sm:py-3 text-sm sm:text-base bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all duration-300 touch-target phone-full-width"
                >
                  Export
                </button>
                <button
                  onClick={() => {
                    if (formSubmissionCount === 0) {
                      setEmailModal(true);
                    } else {
                      handleSendEmail();
                    }
                  }}
                  className="w-full sm:w-auto px-4 sm:px-6 py-2.5 sm:py-3 text-sm sm:text-base bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all duration-300 touch-target phone-full-width"
                >
                  Send Email
                </button>
              </div>
            </div>
          )}
        </div>
        
        <DocumentPreviewModal
          isOpen={previewModal.isOpen}
          onClose={closePreviewModal}
          fileId={previewModal.fileId}
          extractedData={previewModal.extractedData}
          filename={previewModal.filename}
        />
        
        <FormModal
          isOpen={saveModal}
          onClose={() => setSaveModal(false)}
          onSubmit={(data) => {
            setSavedFormData(data);
            setFormSubmissionCount(1);
            handleSave(data);
            setSaveModal(false);
          }}
          title="Enter Details"
        />
        
        <FormModal
          isOpen={emailModal}
          onClose={() => setEmailModal(false)}
          onSubmit={(data) => {
            setSavedFormData(data);
            setFormSubmissionCount(1);
            handleSendEmail(data);
            setEmailModal(false);
          }}
          title="Enter Details"
        />
        

      </main>
    </div>
  );
};

export default Index;
