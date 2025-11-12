import React, { useState } from 'react';
import { Edit2, Save, X } from 'lucide-react';

interface ExtractedData {
  name: string;
  phone: string;
  email: string;
  company: string;
  designation: string;
  address: string;
}

interface DataTableProps {
  data: ExtractedData[];
  onDataChange: (updatedData: ExtractedData[]) => void;
}

const DataTable: React.FC<DataTableProps> = ({ data, onDataChange }) => {
  const [editingCell, setEditingCell] = useState<{ row: number; field: string } | null>(null);
  const [editValue, setEditValue] = useState('');

  const fields = [
    { key: 'name', label: 'Name' },
    { key: 'phone', label: 'Phone' },
    { key: 'email', label: 'Email' },
    { key: 'company', label: 'Company' },
    { key: 'designation', label: 'Designation' },
    { key: 'address', label: 'Address' }
  ];

  const handleEdit = (rowIndex: number, field: string, currentValue: string) => {
    setEditingCell({ row: rowIndex, field });
    setEditValue(currentValue);
  };

  const handleSave = () => {
    if (!editingCell) return;
    
    const updatedData = [...data];
    updatedData[editingCell.row] = {
      ...updatedData[editingCell.row],
      [editingCell.field]: editValue
    };
    
    onDataChange(updatedData);
    setEditingCell(null);
    setEditValue('');
  };

  const handleCancel = () => {
    setEditingCell(null);
    setEditValue('');
  };

  if (data.length === 0) return null;

  return (
    <div className="bg-white rounded-lg border shadow-sm">
      <div className="p-4 border-b">
        <h3 className="text-lg font-semibold">Extracted Data</h3>
        <p className="text-sm text-gray-600">Click on any cell to edit the data</p>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-bold text-gray-900">
                Sr No
              </th>
              {fields.map(field => (
                <th key={field.key} className="px-4 py-3 text-left text-sm font-bold text-gray-900">
                  {field.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-900 font-medium">
                  {rowIndex + 1}
                </td>
                {fields.map(field => (
                  <td key={field.key} className="px-4 py-3 text-sm text-gray-900">
                    {editingCell?.row === rowIndex && editingCell?.field === field.key ? (
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          className="flex-1 px-2 py-1 border rounded text-sm"
                          autoFocus
                        />
                        <button
                          onClick={handleSave}
                          className="p-1 text-green-600 hover:bg-green-100 rounded"
                        >
                          <Save className="w-4 h-4" />
                        </button>
                        <button
                          onClick={handleCancel}
                          className="p-1 text-red-600 hover:bg-red-100 rounded"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <div
                        className="cursor-pointer hover:bg-blue-50 p-1 rounded group flex items-center gap-2"
                        onClick={() => handleEdit(rowIndex, field.key, row[field.key as keyof ExtractedData] || '')}
                      >
                        <span className="flex-1">{row[field.key as keyof ExtractedData] || '-'}</span>
                        <Edit2 className="w-3 h-3 text-gray-400 opacity-0 group-hover:opacity-100" />
                      </div>
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DataTable;