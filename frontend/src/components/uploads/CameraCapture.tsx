import { useRef, useState, useCallback, useEffect } from 'react';
import { X, Check } from 'lucide-react';

interface CameraCaptureProps {
  onCapture: (file: File) => void;
  onClose: () => void;
}

const CameraCapture = ({ onCapture, onClose }: CameraCaptureProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [brightness, setBrightness] = useState(100);
  const [contrast, setContrast] = useState(100);

  const startCamera = useCallback(async () => {
    try {
      // Check if camera is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Camera not supported in this browser. Please use Chrome, Firefox, or Edge.');
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setIsStreaming(true);
      }
    } catch (error: any) {
      console.error('Camera error:', error);
      let message = 'Camera access failed. ';
      
      if (error.name === 'NotAllowedError') {
        message = 'Camera permission denied. Please:\n1. Click "Allow" when browser asks for camera\n2. Check browser camera settings\n3. Check Windows privacy settings';
      } else if (error.name === 'NotFoundError') {
        message = 'No camera found. Please connect a camera and try again.';
      } else if (error.name === 'NotSupportedError') {
        message = 'Camera not supported. Please use HTTPS or localhost.';
      } else {
        message += 'Please check:\n1. Camera permissions\n2. Windows privacy settings\n3. Browser compatibility';
      }
      
      alert(message);
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext('2d');

    if (!context) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Apply brightness and contrast
    context.filter = `brightness(${brightness}%) contrast(${contrast}%)`;
    context.drawImage(video, 0, 0);
    context.filter = 'none';

    canvas.toBlob((blob) => {
      if (blob) {
        const imageUrl = URL.createObjectURL(blob);
        setCapturedImage(imageUrl);
        stopCamera();
      }
    }, 'image/jpeg', 0.9);
  };

  const confirmCapture = () => {
    if (!canvasRef.current) return;

    canvasRef.current.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], `camera-${Date.now()}.jpg`, {
          type: 'image/jpeg'
        });
        onCapture(file);
        onClose();
      }
    }, 'image/jpeg', 0.9);
  };

  const retakePhoto = () => {
    setCapturedImage(null);
    startCamera();
  };

  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, [startCamera, stopCamera]);

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-center p-4 bg-black/50">
        <button onClick={onClose} className="p-2 rounded-full bg-white/20 hover:bg-white/30">
          <X className="w-6 h-6 text-white" />
        </button>
        <h2 className="text-white font-semibold">Live Camera</h2>
        <div className="w-6"></div>
      </div>

      {/* Camera View */}
      <div className="flex-1 relative">
        {capturedImage ? (
          <img src={capturedImage} alt="Captured" className="w-full h-full object-cover" />
        ) : (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
            style={{
              filter: `brightness(${brightness}%) contrast(${contrast}%)`
            }}
          />
        )}
        
        {/* Camera Controls */}
        {isStreaming && !capturedImage && (
          <div className="absolute top-4 right-4 bg-black/60 rounded-lg p-3 space-y-2">
            <div className="text-white text-xs">
              <div className="mb-1">Brightness: {brightness}%</div>
              <input
                type="range"
                min="50"
                max="150"
                value={brightness}
                onChange={(e) => setBrightness(Number(e.target.value))}
                className="w-20 h-1 bg-gray-300 rounded-lg appearance-none cursor-pointer"
              />
            </div>
            <div className="text-white text-xs">
              <div className="mb-1">Contrast: {contrast}%</div>
              <input
                type="range"
                min="50"
                max="150"
                value={contrast}
                onChange={(e) => setContrast(Number(e.target.value))}
                className="w-20 h-1 bg-gray-300 rounded-lg appearance-none cursor-pointer"
              />
            </div>
          </div>
        )}
        
        {!isStreaming && !capturedImage && (
          <div className="absolute inset-0 flex items-center justify-center">
            <button
              onClick={startCamera}
              className="px-6 py-3 bg-navy-primary text-white rounded-lg"
            >
              Start Camera
            </button>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="p-4 bg-black/50">
        {capturedImage ? (
          <div className="flex justify-center gap-4">
            <button
              onClick={retakePhoto}
              className="px-6 py-3 bg-gray-600 text-white rounded-lg"
            >
              Retake
            </button>
            <button
              onClick={confirmCapture}
              className="px-6 py-3 bg-green-600 text-white rounded-lg flex items-center"
            >
              <Check className="w-5 h-5 mr-2" />
              Use Photo
            </button>
          </div>
        ) : (
          isStreaming && (
            <div className="flex flex-col items-center space-y-3">
              <div className="flex justify-center">
                <button
                  onClick={capturePhoto}
                  className="w-16 h-16 bg-white rounded-full border-4 border-gray-300 hover:border-gray-400 flex items-center justify-center"
                >
                  <div className="w-12 h-12 bg-navy-primary rounded-full"></div>
                </button>
              </div>
              <div className="text-white/60 text-xs text-center">
                Adjust brightness/contrast using controls in top-right corner
              </div>
            </div>
          )
        )}
      </div>

      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
};

export default CameraCapture;