import React, { createContext, useContext, useState } from "react";

type ToastType = "info" | "success" | "error";
type ToastItem = { id: number; message: string; type: ToastType };

const ToastCtx = createContext<(msg: string, type?: ToastType) => void>(
  () => {}
);

export const useToast = () => useContext(ToastCtx);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [items, setItems] = useState<ToastItem[]>([]);

  const show = (message: string, type: ToastType = "info") => {
    const id = Date.now() + Math.random();
    setItems((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setItems((prev) => prev.filter((t) => t.id !== id)), 3000);
  };

  const color = (type: ToastType) =>
    type === "success"
      ? "bg-green-600"
      : type === "error"
      ? "bg-red-600"
      : "bg-neutral-900";

  const Icon = ({ type }: { type: ToastType }) => (
    <span className="inline-flex items-center justify-center w-4 h-4 text-[10px] font-bold">
      {type === "success" ? "✓" : type === "error" ? "!" : "i"}
    </span>
  );

  return (
    <ToastCtx.Provider value={show}>
      {children}
      <div className="fixed bottom-4 right-4 space-y-2 z-50">
        {items.map((t) => (
          <div
            key={t.id}
            className={`px-3 py-2 rounded-md text-white shadow flex items-center gap-2 ${color(
              t.type
            )}`}
          >
            <Icon type={t.type} />
            <span className="text-sm">{t.message}</span>
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  );
};
