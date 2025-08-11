import {useToast} from '@/components/Toast';
import {singleInstallCommand} from '@/lib/bundle';
import type {ProgramMeta} from '@/types/data.d.ts';
import React from 'react';

type Props = {
  program: ProgramMeta | null;
  onClose: () => void;
  onToggle: () => void;
  selected: boolean;
};

const AppDetail: React.FC<Props> = ({program, onClose, onToggle, selected}) => {
  const toast = useToast();
  if (!program) return null;
  return (
    <div className="fixed inset-0 z-50 flex">
      <div className="flex-1 bg-black/40" onClick={onClose} />
      <div className="h-full w-[420px] max-w-full overflow-y-auto border-l border-neutral-200 bg-white p-6 dark:border-neutral-800 dark:bg-neutral-900">
        <div className="flex items-center gap-3">
          <img
            src={program.image || '/icons/default-app.svg'}
            alt="icon"
            className="h-12 w-12 rounded"
          />
          <div>
            <h2 className="text-xl font-semibold">{program.name}</h2>
            {program.type === 'shell_script' && <p className="text-xs text-neutral-500">Script</p>}
          </div>
        </div>
        <div className="mt-4 space-y-2 text-sm">
          {program.description && <p className="opacity-80">{program.description}</p>}
          {program.category && (
            <div>
              <span className="text-neutral-500">Category:</span> {program.category}
            </div>
          )}
          {program.tags?.length ? (
            <div className="flex flex-wrap gap-2">
              {program.tags.slice(0, 12).map(t => (
                <span
                  key={t}
                  className="rounded bg-neutral-100 px-2 py-0.5 text-xs dark:bg-neutral-800"
                >
                  {t}
                </span>
              ))}
            </div>
          ) : null}
        </div>
        <div className="mt-6">
          <h3 className="mb-2 text-sm font-medium">Advanced install options</h3>
          <div className="rounded-md border border-neutral-200 p-3 text-sm text-neutral-600 dark:border-neutral-800 dark:text-neutral-300">
            <div className="space-y-3">
              {singleInstallCommand(program) && (
                <div className="flex items-center gap-2">
                  <div className="font-mono text-xs break-all">
                    $ {singleInstallCommand(program)}
                  </div>
                  <button
                    className="rounded border px-2 py-1 text-xs"
                    onClick={() => {
                      navigator.clipboard.writeText(singleInstallCommand(program) || '');
                      toast('Command copied', 'success');
                    }}
                  >
                    Copy
                  </button>
                </div>
              )}
              {program.install && (
                <div>
                  <div className="mb-1 text-xs font-semibold">Install script</div>
                  <div className="flex items-start gap-2">
                    <pre className="flex-1 rounded bg-neutral-100 p-2 text-xs whitespace-pre-wrap dark:bg-neutral-800">
                      {program.install}
                    </pre>
                    <button
                      className="h-fit rounded border px-2 py-1 text-xs"
                      onClick={() => {
                        navigator.clipboard.writeText(program.install || '');
                        toast('Install script copied', 'success');
                      }}
                    >
                      Copy
                    </button>
                  </div>
                </div>
              )}
              {program.configure && (
                <div>
                  <div className="mb-1 text-xs font-semibold">Configure script</div>
                  <div className="flex items-start gap-2">
                    <pre className="flex-1 rounded bg-neutral-100 p-2 text-xs whitespace-pre-wrap dark:bg-neutral-800">
                      {program.configure}
                    </pre>
                    <button
                      className="h-fit rounded border px-2 py-1 text-xs"
                      onClick={() => {
                        navigator.clipboard.writeText(program.configure || '');
                        toast('Configure script copied', 'success');
                      }}
                    >
                      Copy
                    </button>
                  </div>
                </div>
              )}
              {program.validate && (
                <div>
                  <div className="mb-1 text-xs font-semibold">Validate script</div>
                  <div className="flex items-start gap-2">
                    <pre className="flex-1 rounded bg-neutral-100 p-2 text-xs whitespace-pre-wrap dark:bg-neutral-800">
                      {program.validate}
                    </pre>
                    <button
                      className="h-fit rounded border px-2 py-1 text-xs"
                      onClick={() => {
                        navigator.clipboard.writeText(program.validate || '');
                        toast('Validate script copied', 'success');
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
          <button className="rounded-md border px-3 py-2" onClick={onToggle}>
            {selected ? 'Unselect' : 'Select'}
          </button>
          <button className="rounded-md px-3 py-2" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default AppDetail;
