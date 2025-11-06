import { CheckCircle2, FileImage } from "lucide-react";

const InfoSection = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full">
      <div className="bg-white rounded-xl p-3 border border-gray-200 shadow-md hover:shadow-xl transition-all duration-300">
        <div className="flex items-start gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-accent to-navy-primary flex items-center justify-center flex-shrink-0">
            <FileImage className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="font-semibold text-navy-primary mb-1 text-sm">Valid Format</p>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Root folder with images or PDFs directly inside
            </p>
          </div>
        </div>
      </div>
      
      <div className="bg-white rounded-xl p-3 border border-gray-200 shadow-md hover:shadow-xl transition-all duration-300">
        <div className="flex items-start gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-accent to-navy-primary flex items-center justify-center flex-shrink-0">
            <CheckCircle2 className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="font-semibold text-navy-primary mb-1 text-sm">File Limits</p>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Max <span className="font-semibold text-blue-accent">300 files</span>, <span className="font-semibold text-blue-accent">20MB</span> total
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InfoSection;
