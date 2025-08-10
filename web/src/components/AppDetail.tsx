import React from "react";
import type { ProgramMeta } from "@/types/data.d.ts";
import { singleInstallCommand } from "@/lib/bundle";
import { useToast } from "@/components/Toast";

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
  const toast = useToast();
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
          {program.description && (
            <p className="opacity-80">{program.description}</p>
          )}
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
            <div className="space-y-3">
              {singleInstallCommand(program) && (
                <div className="flex items-center gap-2">
                  <div className="font-mono text-xs break-all">
                    $ {singleInstallCommand(program)}
                  </div>
                  <button
                    className="text-xs px-2 py-1 rounded border"
                    onClick={() => {
                      navigator.clipboard.writeText(
                        singleInstallCommand(program) || ""
                      );
                      toast("Command copied", "success");
                    }}
                  >
                    Copy
                  </button>
                </div>
              )}
              {program.installScript && (
                <div>
                  <div className="text-xs font-semibold mb-1">
                    Install script
                  </div>
                  <div className="flex items-start gap-2">
                    <pre className="flex-1 whitespace-pre-wrap text-xs bg-neutral-100 dark:bg-neutral-800 p-2 rounded">
                      {program.installScript}
                    </pre>
                    <button
                      className="text-xs px-2 py-1 rounded border h-fit"
                      onClick={() => {
                        navigator.clipboard.writeText(
                          program.installScript || ""
                        );
                        toast("Install script copied", "success");
                      }}
                    >
                      Copy
                    </button>
                  </div>
                </div>
              )}
              {program.configureScript && (
                <div>
                  <div className="text-xs font-semibold mb-1">
                    Configure script
                  </div>
                  <div className="flex items-start gap-2">
                    <pre className="flex-1 whitespace-pre-wrap text-xs bg-neutral-100 dark:bg-neutral-800 p-2 rounded">
                      {program.configureScript}
                    </pre>
                    <button
                      className="text-xs px-2 py-1 rounded border h-fit"
                      onClick={() => {
                        navigator.clipboard.writeText(
                          program.configureScript || ""
                        );
                        toast("Configure script copied", "success");
                      }}
                    >
                      Copy
                    </button>
                  </div>
                </div>
              )}
              {program.validateScript && (
                <div>
                  <div className="text-xs font-semibold mb-1">
                    Validate script
                  </div>
                  <div className="flex items-start gap-2">
                    <pre className="flex-1 whitespace-pre-wrap text-xs bg-neutral-100 dark:bg-neutral-800 p-2 rounded">
                      {program.validateScript}
                    </pre>
                    <button
                      className="text-xs px-2 py-1 rounded border h-fit"
                      onClick={() => {
                        navigator.clipboard.writeText(
                          program.validateScript || ""
                        );
                        toast("Validate script copied", "success");
                      }}
                    >
                      Copy
                    </button>
                  </div>
                </div>
              )}
            </div>
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
