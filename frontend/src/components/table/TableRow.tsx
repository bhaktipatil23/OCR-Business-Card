import { Check, X, Clock, Loader2 } from "lucide-react";
import { formatFileSize, getFileExtension } from "@/utils/formatters";

export interface ExtractedData {
  name: string;
  phone: string;
  email: string;
  company: string;
  designation: string;
  address: string;
}

export interface ValidationResult {
  is_business_card: boolean;
  confidence: string;
  reasoning: string;
  information_found: string[];
  raw_response: string;
}

export interface FileData {
  id: string;
  name: string;
  size: number;
  type: string;
  path: string;
  status: "pending" | "uploaded" | "validating" | "valid" | "invalid" | "processing" | "completed" | "success" | "failed" | "error";
  uploadedAt: Date;
  parent: string | null;
  extractedData?: ExtractedData[];
  validation?: ValidationResult;
}

interface TableRowProps {
  file: FileData;
  index: number;
  onFileClick?: (fileId: string) => void;
}

const TableRow = ({ file, index, onFileClick }: TableRowProps) => {
  const getStatusBadge = (status: FileData["status"]) => {
    const configs = {
      pending: {
        color: "bg-yellow-500/10 text-yellow-600 border-yellow-500/20",
        icon: <Clock size={14} />,
        label: "Pending",
      },
      uploaded: {
        color: "bg-blue-500/10 text-blue-600 border-blue-500/20",
        icon: <Check size={14} />,
        label: "Uploaded",
      },
      validating: {
        color: "bg-purple-500/10 text-purple-600 border-purple-500/20",
        icon: <Loader2 size={14} className="animate-spin" />,
        label: "Validating",
      },
      valid: {
        color: "bg-green-500/10 text-green-600 border-green-500/20",
        icon: <Check size={14} />,
        label: "Valid Card",
      },
      invalid: {
        color: "bg-red-500/10 text-red-600 border-red-500/20",
        icon: <X size={14} />,
        label: "Not Business Card",
      },
      processing: {
        color: "bg-blue-500/10 text-blue-600 border-blue-500/20",
        icon: <Loader2 size={14} className="animate-spin" />,
        label: "Processing",
      },
      completed: {
        color: "bg-green-500/10 text-green-600 border-green-500/20",
        icon: <Check size={14} />,
        label: "Completed",
      },
      success: {
        color: "bg-green-500/10 text-green-600 border-green-500/20",
        icon: <Check size={14} />,
        label: "Success",
      },
      failed: {
        color: "bg-red-500/10 text-red-600 border-red-500/20",
        icon: <X size={14} />,
        label: "Failed",
      },
      error: {
        color: "bg-red-500/10 text-red-600 border-red-500/20",
        icon: <X size={14} />,
        label: "Error",
      },
    };

    const config = configs[status] || configs.pending;

    return (
      <span
        className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border ${config.color}`}
      >
        {config.icon}
        {config.label}
      </span>
    );
  };

  return (
    <>
      <tr className="border-b border-border/30 hover:bg-navy-primary/5 transition-all duration-200">
        <td className="p-4 text-foreground font-medium">{index + 1}</td>
        <td className="p-4 text-foreground font-medium">
          <div className="flex flex-col">
            <button
              onClick={() => onFileClick?.(file.id)}
              className="text-left hover:text-blue-600 hover:underline transition-colors"
            >
              {file.name}
            </button>
            {file.validation && file.status === "invalid" && (
              <div className="text-xs text-red-600 mt-1 max-w-xs truncate" title={file.validation.reasoning}>
                {file.validation.reasoning}
              </div>
            )}
            {file.validation && file.status === "valid" && file.validation.confidence && (
              <div className="text-xs text-green-600 mt-1">
                Confidence: {file.validation.confidence}
              </div>
            )}
          </div>
        </td>
        <td className="p-4 text-muted-foreground">{formatFileSize(file.size)}</td>
        <td className="p-4 text-muted-foreground uppercase text-xs font-semibold">{getFileExtension(file.name)}</td>
        <td className="p-4">{getStatusBadge(file.status)}</td>
      </tr>

    </>
  );
};

export default TableRow;
