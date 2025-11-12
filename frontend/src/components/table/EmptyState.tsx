import { ImageOff } from "lucide-react";

const EmptyState = () => {
  return (
    <tr>
      <td colSpan={5} className="p-16">
        <div className="flex flex-col items-center justify-center text-center space-y-4">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-muted/50 to-muted/30 flex items-center justify-center">
            <ImageOff size={40} className="text-muted-foreground/50" />
          </div>
          <div className="space-y-2">
            <p className="text-lg font-semibold text-foreground">No images uploaded yet</p>
            <p className="text-sm text-muted-foreground">Upload a folder with images to see them listed here</p>
          </div>
        </div>
      </td>
    </tr>
  );
};

export default EmptyState;
