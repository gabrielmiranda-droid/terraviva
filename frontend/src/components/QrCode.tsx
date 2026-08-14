import QRCode from "qrcode";
import { useEffect, useState } from "react";

type QrCodeProps = {
  value: string;
  size?: number;
};

export function QrCode({ value, size = 112 }: QrCodeProps) {
  const [src, setSrc] = useState<string>("");

  useEffect(() => {
    let cancelled = false;
    QRCode.toDataURL(value, { width: size, margin: 1, errorCorrectionLevel: "M" }).then((dataUrl) => {
      if (!cancelled) setSrc(dataUrl);
    });
    return () => {
      cancelled = true;
    };
  }, [size, value]);

  if (!src) {
    return <div className="rounded-md border border-stone-300 bg-stone-100" style={{ height: size, width: size }} />;
  }

  return <img alt="QR Code" height={size} src={src} width={size} />;
}
