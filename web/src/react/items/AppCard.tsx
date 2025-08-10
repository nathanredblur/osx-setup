import React from "react";
import { Cog, ExternalLink, DollarSign } from "lucide-react";
import { useSelectionStore } from "../../stores/selection";
import type { ProgramMeta } from "../types.d.ts";

type Props = { program: ProgramMeta };

const AppCard: React.FC<Props> = ({ program }) => {
  const toggle = useSelectionStore((s) => s.toggle);
  const selected = useSelectionStore((s) => Boolean(s.selectedIds[program.id]));

  return (
    <div className="group rounded-xl border border-neutral-800/60 bg-[#0f131a] text-neutral-200 overflow-hidden hover:border-blue-500/60 hover:shadow-lg transition cursor-pointer">
      <div className="p-5 flex gap-4">
        <img
          src={program.icon || "/icons/default-app.svg"}
          alt="icon"
          className="w-14 h-14 rounded-lg object-cover bg-neutral-800/50"
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold truncate text-[15px]">
              {program.name}
            </h3>
            {program.version && (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-neutral-800/60 border border-neutral-700/60">
                {program.version}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 mt-2 text-neutral-400">
            {program.paid && (
              <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border border-emerald-500/40 text-emerald-400 bg-emerald-500/10">
                <DollarSign className="w-3 h-3" /> Paid
              </span>
            )}
            {program.hasSettings && (
              <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border border-sky-500/40 text-sky-300 bg-sky-500/10">
                <Cog className="w-3 h-3" /> Settings
              </span>
            )}
          </div>
        </div>
        <div className="flex items-start gap-2">
          {program.url && (
            <a
              href={program.url}
              target="_blank"
              rel="noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="p-2 rounded-md bg-neutral-800/60 hover:bg-neutral-700/60"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
          )}
          <button
            className={`px-3 py-1.5 text-xs rounded-md border transition ${
              selected
                ? "border-blue-500 text-blue-400 bg-blue-500/10"
                : "border-neutral-700 text-neutral-300 hover:bg-neutral-800/60"
            }`}
            onClick={(e) => {
              e.stopPropagation();
              toggle(program);
            }}
          >
            {selected ? "Selected" : "Select"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AppCard;
