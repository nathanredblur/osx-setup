import {useToast} from '@/components/Toast';
import {useCatalog} from '@/context/DataContext';
import {
  downloadAllAsZip,
  downloadBrewfile,
  downloadCustomInstall,
  downloadMacSnap,
  downloadPostConfig,
} from '@/lib/download';
import {useModalStore} from '@/stores/modal';
import {useParametersStore} from '@/stores/parameters';
import {useSelectionStore} from '@/stores/selection';
import React, {useEffect, useMemo, useState} from 'react';
import {Button} from './ui/button';

const isEqual = (a: any, b: any) => {
  return JSON.stringify(a) === JSON.stringify(b);
};

const SummaryPanel: React.FC = () => {
  const selectedIds = useSelectionStore(s => s.selectedIds);
  const [showDownloadOptions, setShowDownloadOptions] = useState(false);
  const {programs, categories} = useCatalog();
  const {validationState: initialValidationState} = useParametersStore();
  const {openAppDetail} = useModalStore();
  const [validationState, setValidationState] = useState<Record<
    string,
    {isValid: boolean; errors: string[]}
  > | null>(null);

  useEffect(() => {
    setValidationState(initialValidationState);
  }, [initialValidationState]);

  useEffect(() => {
    const unsubscribe = useParametersStore.subscribe(
      state => state.validationState,
      state => {
        setValidationState(state);
      },
      {equalityFn: isEqual}
    );

    return () => {
      unsubscribe();
    };
  }, []);

  const selectedPrograms = useMemo(() => {
    const ids = Object.keys(selectedIds);
    return programs.filter(program => ids.includes(program.id));
  }, [selectedIds, programs]);

  // Check for apps with missing required parameters
  const appsWithMissingParams = useMemo(() => {
    return selectedPrograms.filter(program => {
      if (!program.parameters || program.parameters.length === 0) return false;
      return validationState?.[program.id]?.isValid === false;
    });
  }, [selectedPrograms, validationState]);

  const total = selectedPrograms.length;
  const toast = useToast();

  async function handleCreateSetup() {
    if (selectedPrograms.length === 0) {
      toast('Nothing selected');
      return;
    }

    if (appsWithMissingParams.length > 0) {
      toast(
        `Please configure parameters for: ${appsWithMissingParams.map(p => p.name).join(', ')}`,
        'error'
      );
      return;
    }

    try {
      await downloadAllAsZip(selectedPrograms);
      toast('MacSnap setup ZIP downloaded');
    } catch (error) {
      toast('Error creating setup ZIP');
    }
  }

  // Funciones para las nuevas descargas
  const handleDownloadBrewfile = () => {
    if (selectedPrograms.length === 0) {
      toast('Nothing selected');
      return;
    }
    downloadBrewfile(selectedPrograms);
    toast('Brewfile downloaded');
  };

  const handleDownloadPostConfig = () => {
    if (selectedPrograms.length === 0) {
      toast('Nothing selected');
      return;
    }

    if (appsWithMissingParams.length > 0) {
      toast(
        `Please configure parameters for: ${appsWithMissingParams.map(p => p.name).join(', ')}`,
        'error'
      );
      return;
    }

    downloadPostConfig(selectedPrograms);
    toast('postConfig.sh downloaded');
  };

  const handleDownloadCustomInstall = () => {
    if (selectedPrograms.length === 0) {
      toast('Nothing selected');
      return;
    }
    downloadCustomInstall(selectedPrograms);
    toast('customInstall.sh downloaded');
  };

  const handleDownloadMacSnap = async () => {
    try {
      await downloadMacSnap();
      toast('macSnap.sh downloaded');
    } catch (error) {
      toast('Error downloading macSnap.sh');
    }
  };

  const byCategory = useMemo(() => {
    const map: Record<string, number> = {};
    for (const p of selectedPrograms) {
      const key = p.category || 'Uncategorized';
      map[key] = (map[key] || 0) + 1;
    }
    return map;
  }, [selectedPrograms]);

  return (
    <aside className="flex h-full w-96 shrink-0 flex-col border-l border-neutral-200 bg-neutral-50 dark:border-neutral-800 dark:bg-[#0f131a]">
      <div className="border-b border-neutral-200 p-4 dark:border-neutral-800">
        <h2 className="text-sm font-semibold tracking-wide text-neutral-500 uppercase">Summary</h2>
      </div>
      <div className="space-y-4 p-4 text-sm">
        <div>
          <div className="flex items-center justify-between">
            <span>Selected</span>
            <span className="font-medium">{total}</span>
          </div>
          <div className="mt-2 h-2 rounded bg-neutral-800/40">
            <div className="h-2 rounded bg-blue-600" style={{width: `${Math.min(100, total)}%`}} />
          </div>
        </div>
        <div className="space-y-2">
          {/* Botón principal - mantener funcionalidad original */}
          <Button
            variant="primary"
            onClick={handleCreateSetup}
            className="w-full py-3 font-semibold"
          >
            📦 Download Setup ZIP
          </Button>

          {/* Botón para mostrar opciones avanzadas */}
          <Button
            variant="outline"
            onClick={() => setShowDownloadOptions(!showDownloadOptions)}
            className="w-full"
          >
            {showDownloadOptions ? '🔼 Hide' : '🔽 Show'} Advanced Options
          </Button>

          {/* Opciones de descarga expandibles */}
          {showDownloadOptions && (
            <div className="space-y-2 rounded-md border border-neutral-200 bg-white p-3 dark:border-neutral-700 dark:bg-neutral-800">
              <div className="text-xs font-semibold tracking-wide text-neutral-500 uppercase">
                Individual Files
              </div>
              <div className="grid grid-cols-2 gap-2">
                <Button onClick={handleDownloadBrewfile} variant="success" size="sm">
                  Brewfile
                </Button>
                <Button onClick={handleDownloadPostConfig} variant="warning" size="sm">
                  PostConfig
                </Button>
                <Button
                  onClick={handleDownloadCustomInstall}
                  className="bg-purple-600 text-white hover:bg-purple-500"
                  size="sm"
                >
                  Custom Install
                </Button>
                <Button
                  onClick={handleDownloadMacSnap}
                  className="bg-indigo-600 text-white hover:bg-indigo-500"
                  size="sm"
                >
                  MacSnap
                </Button>
              </div>
            </div>
          )}
        </div>

        <div className="pt-2">
          <div className="mb-2 text-xs tracking-wide text-neutral-500 uppercase">By category</div>
          <div className="space-y-1">
            {Object.keys(byCategory).length === 0 && (
              <div className="text-neutral-500">No selection</div>
            )}
            {categories.map(c => (
              <div key={c} className="flex justify-between">
                <span>{c}</span>
                <span className="font-medium">{byCategory[c] || 0}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Apps with missing parameters warning */}
        {appsWithMissingParams.length > 0 && (
          <div className="pt-2">
            <div className="mb-2 rounded-md bg-yellow-50 p-3 dark:bg-yellow-900/20">
              <div className="text-sm text-yellow-800 dark:text-yellow-200">
                <div className="flex items-center gap-1 font-medium">
                  <span>⚠️</span>
                  Configuration Required
                </div>
                <div className="mt-1 text-xs">
                  {appsWithMissingParams.length} app{appsWithMissingParams.length > 1 ? 's' : ''}{' '}
                  need{appsWithMissingParams.length === 1 ? 's' : ''} configuration before download
                </div>
                <div className="mt-2 space-y-1">
                  {appsWithMissingParams.map(app => (
                    <div key={app.id} className="text-xs">
                      • {app.name}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="pt-2">
          <div className="mb-2 text-xs tracking-wide text-neutral-500 uppercase">Selected apps</div>
          <div className="max-h-64 space-y-2 overflow-auto pr-2">
            {selectedPrograms.map(p => {
              const needsConfig = appsWithMissingParams.some(app => app.id === p.id);
              return (
                <div
                  key={p.id}
                  className={`flex items-center justify-between rounded px-2 py-1 ${
                    needsConfig
                      ? 'border border-yellow-200 bg-yellow-100 dark:border-yellow-800 dark:bg-yellow-900/20'
                      : 'bg-neutral-900/40'
                  }`}
                >
                  <div
                    className="flex cursor-pointer items-center gap-2 truncate text-sm hover:opacity-80"
                    title={p.name}
                    onClick={() => openAppDetail(p.id)}
                  >
                    {needsConfig && (
                      <span className="text-yellow-600 dark:text-yellow-400">⚠️</span>
                    )}
                    <span className={needsConfig ? 'text-yellow-800 dark:text-yellow-200' : ''}>
                      {p.name}
                    </span>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => useSelectionStore.getState().toggle(p)}
                  >
                    Remove
                  </Button>
                </div>
              );
            })}
            {selectedPrograms.length === 0 && (
              <div className="text-neutral-500">Nothing selected yet</div>
            )}
          </div>
        </div>
      </div>
    </aside>
  );
};

export default SummaryPanel;
