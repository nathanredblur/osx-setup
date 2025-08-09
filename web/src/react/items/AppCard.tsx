import React from "react";
import { Cog, ExternalLink, DollarSign } from "lucide-react";
import { useSelectionStore } from "../../stores/selection";
import type { ProgramMeta } from "../types.d.ts";

type Props = { program: ProgramMeta };

const AppCard: React.FC<Props> = ({ program }) => {
  const toggle = useSelectionStore((s) => s.toggle);
  const selected = useSelectionStore((s) => Boolean(s.selectedIds[program.id]));

  return (
    <div className="group rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 overflow-hidden hover:shadow-md transition cursor-pointer">
      <div className="p-4 flex gap-3">
        <img
          src={program.icon || "/icons/default-app.svg"}
          alt="icon"
          className="w-12 h-12 rounded-md object-cover bg-neutral-200 dark:bg-neutral-800"
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-medium truncate">{program.name}</h3>
            {program.version && (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-neutral-100 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700">
                {program.version}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 mt-2 text-neutral-500">
            {program.paid && <DollarSign className="w-4 h-4" />}
            {program.url && (
              <a
                href={program.url}
                target="_blank"
                rel="noreferrer"
                onClick={(e) => e.stopPropagation()}
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            )}
            {program.hasSettings && <Cog className="w-4 h-4" />}
          </div>
        </div>
        <div className="flex items-start">
          <button
            className={`px-2 py-1 text-sm rounded-md border hover:bg-neutral-100 dark:hover:bg-neutral-800 ${
              selected
                ? "border-blue-600 text-blue-600"
                : "border-neutral-300 dark:border-neutral-700"
            }`}
            onClick={(e) => {
              e.stopPropagation();
              toggle(program);
            }}
          >
            {selected ? "Unselect" : "Select"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AppCard;
