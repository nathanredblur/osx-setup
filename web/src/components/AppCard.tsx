import React from "react";
import { Cog, ExternalLink, DollarSign } from "lucide-react";
import { useSelectionStore } from "@/stores/selection";
import type { ProgramMeta } from "@/types/data.d.ts";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

type Props = { program: ProgramMeta };

const AppCard: React.FC<Props> = ({ program }) => {
  const toggle = useSelectionStore((s) => s.toggle);
  const selected = useSelectionStore((s) => Boolean(s.selectedIds[program.id]));

  return (
    <div className="group rounded-2xl border border-neutral-800/60 bg-[#0f131a] text-neutral-200 overflow-hidden hover:border-blue-500/60 hover:shadow-lg transition cursor-pointer min-w-[350px]">
      <div className="p-5 grid grid-cols-[64px_1fr] gap-4 items-center">
        <img
          src={program.icon || "/icons/default-app.svg"}
          alt="icon"
          className="w-16 h-16 rounded-xl object-cover bg-neutral-800/50"
        />
        <div className="min-w-0 flex flex-col gap-2">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-semibold text-[15px] leading-5 break-words">
              {program.name}
            </h3>
            <div className="flex items-center gap-2">
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
              <Button
                variant="outline"
                className={
                  selected ? "h-8 border-blue-500 text-blue-400" : "h-8"
                }
                onClick={(e) => {
                  e.stopPropagation();
                  toggle(program);
                }}
              >
                {selected ? "Selected" : "Select"}
              </Button>
            </div>
          </div>
          <div className="flex items-center gap-2 text-neutral-400">
            {program.version && (
              <Badge className="border-neutral-700/60 text-[10px]">
                {program.version}
              </Badge>
            )}
            {program.paid && (
              <Badge className="border-emerald-500/40 text-emerald-400 bg-emerald-500/10">
                <DollarSign className="w-3 h-3" /> Paid
              </Badge>
            )}
            {program.hasSettings && (
              <Badge className="border-sky-500/40 text-sky-300 bg-sky-500/10">
                <Cog className="w-3 h-3" /> Settings
              </Badge>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AppCard;
