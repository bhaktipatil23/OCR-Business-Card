import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Edit, Save, Download, X } from "lucide-react";

interface ExtractedData {
  name: string;
  phone: string;
  email: string;
  company: string;
  designation: string;
}

interface ExtractedDataCardProps {
  data: ExtractedData;
  fileName: string;
  onSave: (data: ExtractedData) => void;
  onDownload: () => void;
}

const ExtractedDataCard = ({ data, fileName, onSave, onDownload }: ExtractedDataCardProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState(data);

  const handleSave = () => {
    onSave(editData);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditData(data);
    setIsEditing(false);
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{fileName}</CardTitle>
        <div className="flex gap-2">
          {isEditing ? (
            <>
              <Button size="sm" onClick={handleSave}>
                <Save className="h-4 w-4" />
              </Button>
              <Button size="sm" variant="outline" onClick={handleCancel}>
                <X className="h-4 w-4" />
              </Button>
            </>
          ) : (
            <>
              <Button size="sm" variant="outline" onClick={() => setIsEditing(true)}>
                <Edit className="h-4 w-4" />
              </Button>
              <Button size="sm" onClick={onDownload}>
                <Download className="h-4 w-4" />
              </Button>
            </>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <Label htmlFor="name">Name</Label>
          {isEditing ? (
            <Input
              id="name"
              value={editData.name}
              onChange={(e) => setEditData({ ...editData, name: e.target.value })}
            />
          ) : (
            <p className="text-sm text-muted-foreground">{data.name || "N/A"}</p>
          )}
        </div>
        
        <div>
          <Label htmlFor="phone">Phone</Label>
          {isEditing ? (
            <Input
              id="phone"
              value={editData.phone}
              onChange={(e) => setEditData({ ...editData, phone: e.target.value })}
            />
          ) : (
            <p className="text-sm text-muted-foreground">{data.phone || "N/A"}</p>
          )}
        </div>
        
        <div>
          <Label htmlFor="email">Email</Label>
          {isEditing ? (
            <Input
              id="email"
              value={editData.email}
              onChange={(e) => setEditData({ ...editData, email: e.target.value })}
            />
          ) : (
            <p className="text-sm text-muted-foreground">{data.email || "N/A"}</p>
          )}
        </div>
        
        <div>
          <Label htmlFor="company">Company</Label>
          {isEditing ? (
            <Input
              id="company"
              value={editData.company}
              onChange={(e) => setEditData({ ...editData, company: e.target.value })}
            />
          ) : (
            <p className="text-sm text-muted-foreground">{data.company || "N/A"}</p>
          )}
        </div>
        
        <div>
          <Label htmlFor="designation">Designation</Label>
          {isEditing ? (
            <Input
              id="designation"
              value={editData.designation}
              onChange={(e) => setEditData({ ...editData, designation: e.target.value })}
            />
          ) : (
            <p className="text-sm text-muted-foreground">{data.designation || "N/A"}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ExtractedDataCard;