// Dynamic API base URL that works on different devices
const getApiBaseUrl = () => {
  const hostname = window.location.hostname;
  // If accessing via localhost, use localhost
  // If accessing via IP, use the same IP for backend
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000/api/v1';
  }
  // Use the same IP as frontend but port 8000 for backend
  return `http://${hostname}:8000/api/v1`;
};

const API_BASE_URL = getApiBaseUrl();

export interface ValidationResult {
  is_business_card: boolean;
  confidence: string;
  reasoning: string;
  information_found: string[];
  raw_response: string;
}

export interface FileInfo {
  file_id: string;
  filename: string;
  size: number;
  file_path: string;
  validation?: ValidationResult;
}

export interface UploadResponse {
  status: string;
  batch_id: string;
  uploaded_files: FileInfo[];
  total_count: number;
  message: string;
}

export interface ProcessResponse {
  status: string;
  batch_id: string;
  total_files: number;
  message: string;
}

export interface StatusResponse {
  status: string;
  batch_id: string;
  progress: {
    total_files: number;
    processed: number;
    percentage: number;
  };
  current_file?: string;
}

export interface ValidationResponse {
  status: string;
  batch_id: string;
  validation_summary: {
    total_files: number;
    valid_cards: number;
    invalid_files: number;
  };
  valid_business_cards: number;
  invalid_files: number;
  message: string;
}

export interface ExtractedDataResponse {
  file_id: string;
  filename: string;
  extracted_data: {
    name: string;
    phone: string;
    email: string;
    company: string;
    designation: string;
    address: string;
  }[];
}

class ApiService {
  async uploadFiles(files: File[]): Promise<UploadResponse> {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    return response.json();
  }

  async processFiles(batchId: string): Promise<ProcessResponse> {
    const response = await fetch(`${API_BASE_URL}/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ batch_id: batchId }),
    });

    if (!response.ok) {
      throw new Error(`Processing failed: ${response.statusText}`);
    }

    return response.json();
  }

  async getStatus(batchId: string): Promise<StatusResponse> {
    const response = await fetch(`${API_BASE_URL}/status/${batchId}`);

    if (!response.ok) {
      throw new Error(`Status check failed: ${response.statusText}`);
    }

    return response.json();
  }

  async downloadCsv(batchId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/download/${batchId}`);

    if (!response.ok) {
      throw new Error(`Download failed: ${response.statusText}`);
    }

    return response.blob();
  }

  getDownloadUrl(batchId: string): string {
    return `${API_BASE_URL}/download/${batchId}`;
  }

  async validateFiles(batchId: string): Promise<ValidationResponse> {
    const response = await fetch(`${API_BASE_URL}/validate/${batchId}`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`Validation failed: ${response.statusText}`);
    }

    return response.json();
  }

  async getValidationStatus(batchId: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/validation-status/${batchId}`);

    if (!response.ok) {
      throw new Error(`Failed to get validation status: ${response.statusText}`);
    }

    return response.json();
  }

  async getExtractedData(batchId: string): Promise<ExtractedDataResponse[]> {
    const response = await fetch(`${API_BASE_URL}/extracted-data/${batchId}`);

    if (!response.ok) {
      throw new Error(`Failed to get extracted data: ${response.statusText}`);
    }

    return response.json();
  }
}

export const apiService = new ApiService();