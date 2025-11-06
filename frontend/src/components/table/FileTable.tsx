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
    <div className="backdrop-blur-md bg-white/70 rounded-3xl shadow-2xl p-8 border border-white/50">
      <div className="mb-8 pb-6 border-b border-border/50 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-navy-primary to-blue-accent flex items-center justify-center">
              <AlertCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-sm text-muted-foreground font-medium">Files Detected</h2>
              <p className={`text-2xl font-bold ${getCounterColor()}`}>
                {fileCount} / 300
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
              <AlertCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-sm text-muted-foreground font-medium">Total Size</h2>
              <p className={`text-2xl font-bold ${getSizeColor()}`}>
                {totalSizeMB.toFixed(1)} / 20 MB
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {(validFiles > 0 || invalidFiles > 0) && (
            <div className="flex items-center gap-4">
              {validFiles > 0 && (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 rounded-lg border border-green-500/20">
                  <CheckCircle size={16} className="text-green-600" />
                  <span className="text-sm font-medium text-green-600">{validFiles} Valid</span>
                </div>
              )}
              {invalidFiles > 0 && (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-red-500/10 rounded-lg border border-red-500/20">
                  <XCircle size={16} className="text-red-600" />
                  <span className="text-sm font-medium text-red-600">{invalidFiles} Invalid</span>
                </div>
              )}
            </div>
          )}
          {(isAtLimit || isSizeAtLimit) && (
            <div className="flex items-center gap-2 px-4 py-2 bg-error/10 rounded-xl border border-error/20">
              <AlertCircle size={20} className="text-error" />
              <span className="text-sm font-medium text-error">
                {isAtLimit && isSizeAtLimit ? "File & Size limits reached" : 
                 isAtLimit ? "File limit reached" : "Size limit reached"}
              </span>
            </div>
          )}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[600px]">
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
  );
};

export default FileTable;
