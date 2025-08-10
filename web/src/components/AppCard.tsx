import {Badge} from '@/components/ui/badge';
import {Button} from '@/components/ui/button';
import {useSelectionStore} from '@/stores/selection';
import type {ProgramMeta} from '@/types/data.d.ts';
import {Cog, DollarSign, ExternalLink} from 'lucide-react';
import React from 'react';

type Props = {program: ProgramMeta; onClick: () => void};

const AppCard: React.FC<Props> = ({program, onClick}) => {
  const toggle = useSelectionStore(s => s.toggle);
  const selected = useSelectionStore(s => Boolean(s.selectedIds[program.id]));

  return (
    <div
      className="group grid cursor-pointer grid-cols-[80px_1fr] items-center gap-2 overflow-hidden rounded-2xl border border-neutral-200 bg-white p-2 text-neutral-900 transition duration-150 hover:border-blue-500/60 hover:shadow-lg hover:ring-2 hover:ring-blue-500/20 dark:border-neutral-800/60 dark:bg-[#0f131a] dark:text-neutral-200 dark:hover:border-blue-400/60 dark:hover:bg-[#121826] dark:hover:ring-blue-400/25"
      onClick={onClick}
    >
      <img
        src={program.icon || '/icons/default-app.svg'}
        alt="icon"
        className="h-20 w-20 rounded-xl bg-neutral-100 object-cover dark:bg-neutral-800/50"
      />
      <div className="flex min-w-0 flex-col gap-2">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-[15px] leading-5 font-semibold break-words">{program.name}</h3>
        </div>
        <div className="flex items-center gap-2 text-neutral-400">
          {program.version && (
            <Badge className="border-neutral-300 text-[10px] dark:border-neutral-700/60">
              {program.version}
            </Badge>
          )}
          {program.paid && (
            <Badge className="border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-400">
              <DollarSign className="h-3 w-3" /> Paid
            </Badge>
          )}
          {program.hasSettings && (
            <Badge className="border-sky-300 bg-sky-500/10 text-sky-700 dark:border-sky-500/40 dark:text-sky-300">
              <Cog className="h-3 w-3" /> Settings
            </Badge>
          )}
        </div>
        <div className="flex items-center justify-between">
          {program.url && (
            <a
              href={program.url}
              target="_blank"
              rel="noreferrer"
              onClick={e => e.stopPropagation()}
              className="rounded-md bg-neutral-100 p-2 hover:bg-neutral-200 dark:bg-neutral-800/60 dark:hover:bg-neutral-700/60"
            >
              <ExternalLink className="h-4 w-4" />
            </a>
          )}
          <Button
            variant="outline"
            className={selected ? 'h-8 border-blue-500 text-blue-600 dark:text-blue-400' : 'h-8'}
            onClick={e => {
              e.stopPropagation();
              toggle(program);
            }}
          >
            {selected ? 'Selected' : 'Select'}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default AppCard;
