import React from "react";
import type { ProgramMeta } from "../types.d.ts";

type Props = {
  program: ProgramMeta | null;
  onClose: () => void;
  onToggle: () => void;
  selected: boolean;
};

const AppDetail: React.FC<Props> = ({
  program,
  onClose,
  onToggle,
  selected,
}) => {
  if (!program) return null;
  return (
    <div className="fixed inset-0 z-50 flex">
      <div className="flex-1 bg-black/40" onClick={onClose} />
      <div className="w-[420px] max-w-full h-full bg-white dark:bg-neutral-900 border-l border-neutral-200 dark:border-neutral-800 p-6 overflow-y-auto">
        <div className="flex items-center gap-3">
          <img
            src={program.icon || "/icons/default-app.svg"}
            alt="icon"
            className="w-12 h-12 rounded"
          />
          <div>
            <h2 className="text-xl font-semibold">{program.name}</h2>
            {program.version && (
              <p className="text-xs text-neutral-500">v{program.version}</p>
            )}
          </div>
        </div>
        <div className="mt-4 space-y-2 text-sm">
          {program.category && (
            <div>
              <span className="text-neutral-500">Category:</span>{" "}
              {program.category}
            </div>
          )}
          {program.tags?.length ? (
            <div className="flex flex-wrap gap-2">
              {program.tags.slice(0, 12).map((t) => (
                <span
                  key={t}
                  className="px-2 py-0.5 rounded bg-neutral-100 dark:bg-neutral-800 text-xs"
                >
                  {t}
                </span>
              ))}
            </div>
          ) : null}
        </div>
        <div className="mt-6">
          <h3 className="text-sm font-medium mb-2">Advanced install options</h3>
          <div className="rounded-md border border-neutral-200 dark:border-neutral-800 p-3 text-sm text-neutral-600 dark:text-neutral-300">
            This is a placeholder. Flags, post-install scripts, files and
            variables will be shown here.
          </div>
        </div>
        <div className="mt-6 flex gap-2">
          <button className="px-3 py-2 rounded-md border" onClick={onToggle}>
            {selected ? "Unselect" : "Select"}
          </button>
          <button className="px-3 py-2 rounded-md" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default AppDetail;
