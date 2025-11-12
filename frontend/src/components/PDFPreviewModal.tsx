import React, { useState, useEffect } from 'react';
import { X, Eye, Edit2, Image as ImageIcon } from 'lucide-react';

interface PDFData {
  filename: string;
  page: number;
  document_type: string;
  total_records?: number;
  records?: Array<{
    record_id: number;
    data: {
      // Business card fields
      name?: string;
      phone?: string;
      email?: string;
      company?: string;
      designation?: string;
      address?: string;
      // Delivery challan fields
      category?: string;
      vehicle_number?: string;
      date?: string;
      challan_no?: string;
      transporter_name?: string;
      net_weight?: string;
      consignee?: string;
      consignor?: string;
      from_state?: string;
      to_state?: string;
    };
  }>;
  // Legacy single record support
  data?: {
    name?: string;
    phone?: string;
    email?: string;
    company?: string;
    designation?: string;
    address?: string;
    category?: string;
    vehicle_number?: string;
    date?: string;
    challan_no?: string;
    transporter_name?: string;
    net_weight?: string;
    consignee?: string;
    consignor?: string;
    from_state?: string;
    to_state?: string;
  };
}

interface DocumentPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  fileId: string;
  extractedData?: Array<{
    name: string;
    phone: string;
    email: string;
    company: string;
    designation: string;
    address: string;
  }>;
  filename?: string;
}

const DocumentPreviewModal: React.FC<DocumentPreviewModalProps> = ({ isOpen, onClose, fileId, extractedData, filename }) => {
  const [data, setData] = useState<PDFData | null>(null);
  const [loading, setLoading] = useState(false);
  const [editingField, setEditingField] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');
  const [showImage, setShowImage] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState(0);

  useEffect(() => {
    if (isOpen && fileId) {
      if (extractedData && extractedData.length > 0) {
        // Use existing extracted data
        setData({
          filename: filename || `${fileId}`,
          page: 1,
          document_type: 'business_card',
          records: extractedData.map((item, index) => ({
            record_id: index + 1,
            data: item
          }))
        });
        setLoading(false);
      } else {
        // No extracted data available
        setData({
          filename: filename || `${fileId}`,
          page: 1,
          document_type: 'business_card',
          records: []
        });
        setLoading(false);
      }
    }
  }, [isOpen, fileId, extractedData, filename]);

  const fetchPDFData = async () => {
    setLoading(true);
    try {
      console.log('Fetching data for fileId:', fileId);
      const hostname = window.location.hostname;
      const baseUrl = hostname === 'localhost' || hostname === '127.0.0.1' 
        ? 'http://localhost:8000' 
        : `http://${hostname}:8000`;
      const url = `${baseUrl}/api/v1/preview/${fileId}`;
      console.log('Fetching from URL:', url);
      
      const response = await fetch(url);
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      
      const result = await response.json();
      console.log('Received data:', result);
      setData(result);
    } catch (error) {
      console.error('Failed to fetch document data:', error);
      // Set fallback data for testing
      setData({
        filename: `${fileId}.pdf`,
        page: 1,
        document_type: 'delivery_challan',
        data: {
          category: 'Test Document',
          vehicle_number: 'TEST123',
          date: '15-12-2024',
          challan_no: 'TEST/001',
          transporter_name: 'Test Transport',
          net_weight: '1.0 Tons',
          consignee: 'Test Consignee',
          consignor: 'Test Consignor',
          from_state: 'TEST STATE',
          to_state: 'TEST STATE 2'
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (field: string, currentValue: string) => {
    setEditingField(field);
    setEditValue(currentValue);
  };

  const handleSave = async () => {
    if (!editingField || !data) return;
    
    try {
      const hostname = window.location.hostname;
      const baseUrl = hostname === 'localhost' || hostname === '127.0.0.1' 
        ? 'http://localhost:8000' 
        : `http://${hostname}:8000`;
      const response = await fetch(`${baseUrl}/api/v1/preview/${fileId}/update`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field: editingField, value: editValue })
      });
      
      if (response.ok) {
        setData({
          ...data,
          data: { ...data.data, [editingField]: editValue }
        });
        setEditingField(null);
      }
    } catch (error) {
      console.error('Failed to update field:', error);
    }
  };

  const handleCancel = () => {
    setEditingField(null);
    setEditValue('');
  };

  if (!isOpen) return null;

  const getFields = () => {
    if (data?.document_type === 'business_card') {
      return [
        { key: 'name', label: 'Name', editable: true },
        { key: 'phone', label: 'Phone', editable: true },
        { key: 'email', label: 'Email', editable: true },
        { key: 'company', label: 'Company', editable: true },
        { key: 'designation', label: 'Designation', editable: true },
        { key: 'address', label: 'Address', editable: true }
      ];
    } else {
      return [
        { key: 'category', label: 'Category', editable: false },
        { key: 'vehicle_number', label: 'Vehicle Number', editable: true },
        { key: 'date', label: 'Date', editable: true },
        { key: 'challan_no', label: 'Challan No', editable: true },
        { key: 'transporter_name', label: 'Transporter Name', editable: true },
        { key: 'net_weight', label: 'Net Weight (Tons)', editable: true },
        { key: 'consignee', label: 'Consignee', editable: true },
        { key: 'consignor', label: 'Consignor', editable: true },
        { key: 'from_state', label: 'From State', editable: true },
        { key: 'to_state', label: 'To State', editable: true }
      ];
    }
  };
  
  const fields = getFields();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-lg max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold">{data?.filename || filename || 'Loading...'}</h2>
            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
              Page {data?.page || 1}
            </span>
            <button
              onClick={() => setShowImage(!showImage)}
              className="p-1 hover:bg-gray-100 rounded transition-colors"
              title="Toggle image preview"
            >
              {showImage ? <X className="w-5 h-5 text-gray-500" /> : <Eye className="w-5 h-5 text-gray-500" />}
            </button>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Image Preview */}
          {showImage && (
            <div className="mb-6 border rounded-lg overflow-hidden">
              <div className="bg-gray-50 px-4 py-2 border-b">
                <div className="flex items-center gap-2">
                  <ImageIcon className="w-4 h-4 text-gray-600" />
                  <span className="text-sm font-medium text-gray-700">Document Preview</span>
                </div>
              </div>
              <div className="p-4 bg-white">
                <img
                  src={`${(() => {
                    const hostname = window.location.hostname;
                    return hostname === 'localhost' || hostname === '127.0.0.1' 
                      ? 'http://localhost:8000' 
                      : `http://${hostname}:8000`;
                  })()}/api/v1/preview/${fileId}/image`}
                  alt="Document preview"
                  className="max-w-full h-auto max-h-96 mx-auto border rounded shadow-sm"
                  onLoad={() => console.log('Image loaded successfully')}
                  onError={(e) => {
                    const hostname = window.location.hostname;
                    const baseUrl = hostname === 'localhost' || hostname === '127.0.0.1' 
                      ? 'http://localhost:8000' 
                      : `http://${hostname}:8000`;
                    console.error('Image failed to load:', `${baseUrl}/api/v1/preview/${fileId}/image`);
                    const target = e.target as HTMLImageElement;
                    target.style.display = 'none';
                    target.nextElementSibling?.classList.remove('hidden');
                  }}
                />
                <div className="hidden text-center py-8 text-gray-500">
                  <ImageIcon className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                  <p>Image preview not available</p>
                </div>
              </div>
            </div>
          )}
          {/* Data Fields - Removed card view display */}
          {!showImage && (
            <div className="text-center py-8 text-gray-500">
              <p>Preview available - click the eye icon to view the document image.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentPreviewModal;