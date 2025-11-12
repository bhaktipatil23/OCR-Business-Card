import { User, Phone, Mail, Building, MapPin, Briefcase } from 'lucide-react';

interface ExtractedData {
  name: string;
  phone: string;
  email: string;
  company: string;
  designation: string;
  address: string;
}

interface ExtractedDataDisplayProps {
  data: ExtractedData[];
  fileName: string;
}

const ExtractedDataDisplay = ({ data, fileName }: ExtractedDataDisplayProps) => {
  if (!data || data.length === 0) return null;

  return (
    <div className="mt-4 p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
      {/* Header */}
      <div className="mb-4 pb-3 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800">{fileName}</h3>
        <p className="text-sm text-gray-600">Page 1</p>
        <div className="mt-2">
          <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">Document Type: Business Card</span>
          <span className="inline-block ml-2 px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded">JPEG Image</span>
        </div>
        <p className="text-sm text-gray-600 mt-2">File: {fileName}</p>
        <p className="text-sm font-medium text-gray-800">{data.length} records found</p>
      </div>
      
      {/* Records - Show record numbers first, then only first record details */}
      <div className="space-y-4">
        {/* Record Numbers */}
        <div className="space-y-1">
          {data.map((_, index) => (
            <div key={index} className="text-gray-800 font-medium">
              Record {index + 1}
            </div>
          ))}
        </div>
        
        {/* First Record Details Only */}
        {data.length > 0 && (
          <div className="border-l-4 border-blue-500 pl-4 mt-4">
            <div className="space-y-3">
              <div>
                <span className="font-medium text-gray-700">Name:</span>
                <div className="text-gray-900 font-medium">{data[0].name}</div>
              </div>
              
              <div>
                <span className="font-medium text-gray-700">Phone:</span>
                <div className="text-gray-900">{data[0].phone}</div>
              </div>
              
              <div>
                <span className="font-medium text-gray-700">Email:</span>
                <div className="text-gray-900">{data[0].email}</div>
              </div>
              
              <div>
                <span className="font-medium text-gray-700">Company:</span>
                <div className="text-gray-900">{data[0].company}</div>
              </div>
              
              <div>
                <span className="font-medium text-gray-700">Designation:</span>
                <div className="text-gray-900">{data[0].designation}</div>
              </div>
              
              <div>
                <span className="font-medium text-gray-700">Address:</span>
                <div className="text-gray-900">{data[0].address}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ExtractedDataDisplay;