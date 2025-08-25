import ParameterForm from '@/components/ParameterForm';
import {useToast} from '@/components/Toast';
import {singleInstallCommand} from '@/lib/bundle';
import {useFetchBrew} from '@/lib/useFetchBrew';
import {extractBundleName} from '@/lib/utils';
import {useParametersStore} from '@/stores/parameters';
import {useSelectionStore} from '@/stores/selection';
import type {ProgramMeta} from '@/types/data.d.ts';
import React, {useEffect} from 'react';
import {Button} from './ui/button';

type Props = {
  program: ProgramMeta;
  onClose: () => void;
};

const AppDetail: React.FC<Props> = ({program, onClose}) => {
  const toast = useToast();
  const {brewData, loadingBrew, fetchBrewData} = useFetchBrew();

  const toggle = useSelectionStore(s => s.toggle);
  const selected = useSelectionStore(s => Boolean(s.selectedIds[program.id]));

  const {getValidationState} = useParametersStore();

  // Effect to fetch data when program changes
  useEffect(() => {
    if (program?.bundle && (program.type === 'cask' || program.type === 'brew')) {
      const bundleName = extractBundleName(program.bundle);
      if (bundleName) fetchBrewData(bundleName, program.type);
    }
  }, [program]);

  const isNotValid =
    program.parameters && program.parameters.length > 0 && !getValidationState(program.id).isValid;

  return (
    <div className="fixed inset-0 z-50 flex">
      <div className="flex-1 bg-black/40" onClick={onClose} />
      <div className="h-full w-[420px] max-w-full overflow-y-auto border-l border-neutral-200 bg-white p-6 dark:border-neutral-800 dark:bg-neutral-900">
        <div className="flex items-center gap-3">
          <div className="relative h-12 w-12">
            <img
              src={program.image || '/icons/default-app.svg'}
              alt="icon"
              className="h-12 w-12 rounded"
              onError={e => {
                const target = e.target as HTMLImageElement;
                target.src = '/icons/default-app.svg';
              }}
            />
          </div>
          <div>
            <h2 className="text-xl font-semibold">{program.name}</h2>
            {program.type === 'shell_script' && <p className="text-xs text-neutral-500">Script</p>}
          </div>
        </div>
        <div className="mt-4 space-y-3 text-sm">
          {/* Loading state for Homebrew data */}
          {loadingBrew && (
            <div className="flex items-center gap-2 text-neutral-500">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-neutral-300 border-t-neutral-600"></div>
              <span>Loading Homebrew info...</span>
            </div>
          )}

          {/* Enhanced description with Homebrew data */}
          {brewData?.desc && brewData.desc !== program.description ? (
            <div>
              <p className="font-medium opacity-80">{brewData.desc}</p>
              {program.description && program.description !== brewData.desc && (
                <p className="mt-1 text-xs opacity-60">{program.description}</p>
              )}
            </div>
          ) : program.description ? (
            <p className="opacity-80">{program.description}</p>
          ) : null}

          {/* Homebrew specific information */}
          {brewData && (
            <div className="space-y-2 border-l-2 border-blue-200 pl-3 dark:border-blue-800">
              <div className="text-xs font-medium text-blue-600 dark:text-blue-400">
                Homebrew Info
              </div>

              {brewData.version && (
                <div>
                  <span className="text-neutral-500">Version:</span> {brewData.version}
                </div>
              )}

              {brewData.homepage && (
                <div>
                  <span className="text-neutral-500">Homepage:</span>{' '}
                  <a
                    href={brewData.homepage}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline dark:text-blue-400"
                  >
                    {brewData.homepage}
                  </a>
                </div>
              )}

              {brewData.deprecated && (
                <div className="text-orange-600 dark:text-orange-400">
                  <span className="font-medium">⚠️ Deprecated</span>
                  {brewData.deprecation_reason && (
                    <div className="mt-1 text-xs">{brewData.deprecation_reason}</div>
                  )}
                </div>
              )}

              {brewData.caveats && (
                <div className="text-yellow-600 dark:text-yellow-400">
                  <div className="text-xs font-medium">Installation Notes:</div>
                  <pre className="mt-1 text-xs whitespace-pre-wrap">{brewData.caveats}</pre>
                </div>
              )}
            </div>
          )}

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

        {/* Parameters Form */}
        {program.parameters && program.parameters.length > 0 && (
          <div className="mt-6">
            <ParameterForm appId={program.id} parameters={program.parameters} />
          </div>
        )}

        <div className="mt-6">
          <h3 className="mb-2 text-sm font-medium">Advanced install options</h3>
          <div className="rounded-md border border-neutral-200 p-3 text-sm text-neutral-600 dark:border-neutral-800 dark:text-neutral-300">
            <div className="space-y-3">
              {singleInstallCommand(program) && (
                <div className="flex items-center gap-2">
                  <div className="font-mono text-xs break-all">
                    $ {singleInstallCommand(program)}
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      navigator.clipboard.writeText(singleInstallCommand(program) || '');
                      toast('Command copied', 'success');
                    }}
                  >
                    Copy
                  </Button>
                </div>
              )}
              {program.install && (
                <div>
                  <div className="mb-1 text-xs font-semibold">Install script</div>
                  <div className="flex items-start gap-2">
                    <pre className="flex-1 rounded bg-neutral-100 p-2 text-xs whitespace-pre-wrap dark:bg-neutral-800">
                      {program.install}
                    </pre>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        navigator.clipboard.writeText(program.install || '');
                        toast('Install script copied', 'success');
                      }}
                    >
                      Copy
                    </Button>
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
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        navigator.clipboard.writeText(program.configure || '');
                        toast('Configure script copied', 'success');
                      }}
                    >
                      Copy
                    </Button>
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
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        navigator.clipboard.writeText(program.validate || '');
                        toast('Validate script copied', 'success');
                      }}
                    >
                      Copy
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="mt-6 flex flex-col gap-2">
          <div className="flex gap-2">
            <Button
              variant={selected ? 'outline' : 'default'}
              onClick={e => {
                e.stopPropagation();
                toggle(program);
              }}
              disabled={isNotValid}
              title={isNotValid ? 'Please fill in all required parameters first' : undefined}
            >
              {selected ? 'Unselect' : 'Select'}
            </Button>
            <Button variant="ghost" onClick={onClose}>
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AppDetail;
