import TableHeader from "./TableHeader";
import TableRow, { FileData } from "./TableRow";
import EmptyState from "./EmptyState";
import { AlertCircle, CheckCircle, XCircle } from "lucide-react";

interface FileTableProps {
  files: FileData[];
  onFileClick?: (fileId: string) => void;
}

const FileTable = ({ files, onFileClick }: FileTableProps) => {
  const fileCount = files.length;
  const isNearLimit = fileCount >= 250 && fileCount < 300;
  const isAtLimit = fileCount >= 300;
  
  // Calculate total size
  const totalSizeBytes = files.reduce((sum, file) => sum + file.size, 0);
  const totalSizeMB = totalSizeBytes / (1024 * 1024);
  const maxSizeMB = 20;
  const isSizeNearLimit = totalSizeMB >= 16 && totalSizeMB < 20;
  const isSizeAtLimit = totalSizeMB >= 20;
  
  // Validation statistics
  const validFiles = files.filter(f => f.status === "valid" || f.status === "processing" || f.status === "completed").length;
  const invalidFiles = files.filter(f => f.status === "invalid").length;
  const pendingValidation = files.filter(f => f.status === "uploaded" || f.status === "validating").length;

  const getCounterColor = () => {
    if (isAtLimit) return "text-error";
    if (isNearLimit) return "text-warning";
    return "text-foreground";
  };
  
  const getSizeColor = () => {
    if (isSizeAtLimit) return "text-error";
    if (isSizeNearLimit) return "text-warning";
    return "text-foreground";
  };

  return (
    <div className="backdrop-blur-md bg-white/70 rounded-2xl sm:rounded-3xl shadow-2xl p-3 sm:p-6 lg:p-8 border border-white/50">
      {/* Mobile-first header layout */}
      <div className="mb-4 sm:mb-6 lg:mb-8 pb-4 sm:pb-6 border-b border-border/50">
        {/* Stats section - stacked on mobile, side by side on larger screens */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 sm:gap-6">
          <div className="grid grid-cols-2 sm:flex sm:items-center gap-3 sm:gap-6 lg:gap-8">
            <div className="flex items-center gap-2 sm:gap-4">
              <div className="w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12 rounded-lg sm:rounded-xl bg-gradient-to-br from-navy-primary to-blue-accent flex items-center justify-center">
                <AlertCircle className="w-4 h-4 sm:w-5 sm:h-5 lg:w-6 lg:h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xs sm:text-sm text-muted-foreground font-medium">Files</h2>
                <p className={`text-lg sm:text-xl lg:text-2xl font-bold ${getCounterColor()}`}>
                  {fileCount}/300
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 sm:gap-4">
              <div className="w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12 rounded-lg sm:rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <AlertCircle className="w-4 h-4 sm:w-5 sm:h-5 lg:w-6 lg:h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xs sm:text-sm text-muted-foreground font-medium">Size</h2>
                <p className={`text-lg sm:text-xl lg:text-2xl font-bold ${getSizeColor()}`}>
                  {totalSizeMB.toFixed(1)}/20MB
                </p>
              </div>
            </div>
          </div>
          
          {/* Status badges - stacked on mobile */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-4">
            {(validFiles > 0 || invalidFiles > 0) && (
              <div className="flex flex-wrap items-center gap-2">
                {validFiles > 0 && (
                  <div className="flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1 sm:py-1.5 bg-green-500/10 rounded-lg border border-green-500/20">
                    <CheckCircle size={14} className="text-green-600 sm:w-4 sm:h-4" />
                    <span className="text-xs sm:text-sm font-medium text-green-600">{validFiles} Valid</span>
                  </div>
                )}
                {invalidFiles > 0 && (
                  <div className="flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1 sm:py-1.5 bg-red-500/10 rounded-lg border border-red-500/20">
                    <XCircle size={14} className="text-red-600 sm:w-4 sm:h-4" />
                    <span className="text-xs sm:text-sm font-medium text-red-600">{invalidFiles} Invalid</span>
                  </div>
                )}
              </div>
            )}
            {(isAtLimit || isSizeAtLimit) && (
              <div className="flex items-center gap-1 sm:gap-2 px-2 sm:px-3 lg:px-4 py-1 sm:py-2 bg-error/10 rounded-lg sm:rounded-xl border border-error/20">
                <AlertCircle size={16} className="text-error sm:w-5 sm:h-5" />
                <span className="text-xs sm:text-sm font-medium text-error">
                  {isAtLimit && isSizeAtLimit ? "Limits reached" : 
                   isAtLimit ? "File limit" : "Size limit"}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Table with horizontal scroll on mobile */}
      <div className="overflow-x-auto -mx-3 sm:mx-0 phone-table">
        <div className="min-w-[600px] px-3 sm:px-0 phone-full-width">
          <table className="w-full">
            <TableHeader />
            <tbody>
              {files.length === 0 ? (
                <EmptyState />
              ) : (
                files.map((file, index) => (
                  <TableRow key={file.id} file={file} index={index} onFileClick={onFileClick} />
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default FileTable;
