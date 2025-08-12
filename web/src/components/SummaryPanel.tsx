import {useToast} from '@/components/Toast';
import {useCatalog} from '@/context/DataContext';
import {
  downloadAllAsZip,
  downloadBrewfile,
  downloadCustomInstall,
  downloadMacSnap,
  downloadPostConfig,
} from '@/lib/download';
import {useSelectionStore} from '@/stores/selection';
import React, {useMemo, useState} from 'react';

const SummaryPanel: React.FC = () => {
  const selected = useSelectionStore(s => s.selectedIds);
  const [showDownloadOptions, setShowDownloadOptions] = useState(false);
  const total = useMemo(() => {
    const items = Object.values(selected);
    return items.length;
  }, [selected]);

  const toast = useToast();
  const {categories} = useCatalog();

  async function handleCreateSetup() {
    const items = Object.values(selected);
    if (items.length === 0) {
      toast('Nothing selected');
      return;
    }
    try {
      await downloadAllAsZip(items);
      toast('MacSnap setup ZIP downloaded');
    } catch (error) {
      toast('Error creating setup ZIP');
    }
  }

  // Funciones para las nuevas descargas
  const handleDownloadBrewfile = () => {
    const items = Object.values(selected);
    if (items.length === 0) {
      toast('Nothing selected');
      return;
    }
    downloadBrewfile(items);
    toast('Brewfile downloaded');
  };

  const handleDownloadPostConfig = () => {
    const items = Object.values(selected);
    if (items.length === 0) {
      toast('Nothing selected');
      return;
    }
    downloadPostConfig(items);
    toast('postConfig.sh downloaded');
  };

  const handleDownloadCustomInstall = () => {
    const items = Object.values(selected);
    if (items.length === 0) {
      toast('Nothing selected');
      return;
    }
    downloadCustomInstall(items);
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

  const selectedList = Object.values(selected);
  const byCategory = useMemo(() => {
    const map: Record<string, number> = {};
    for (const p of selectedList) {
      const key = p.category || 'Uncategorized';
      map[key] = (map[key] || 0) + 1;
    }
    return map;
  }, [selectedList]);

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
          <button
            onClick={handleCreateSetup}
            className="w-full rounded-md bg-blue-600 py-3 font-semibold text-white hover:bg-blue-500"
          >
            📦 Download Setup ZIP
          </button>

          {/* Botón para mostrar opciones avanzadas */}
          <button
            onClick={() => setShowDownloadOptions(!showDownloadOptions)}
            className="w-full rounded-md border border-neutral-300 bg-white py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-50 dark:border-neutral-600 dark:bg-neutral-800 dark:text-neutral-300 dark:hover:bg-neutral-700"
          >
            {showDownloadOptions ? '🔼 Hide' : '🔽 Show'} Advanced Options
          </button>

          {/* Opciones de descarga expandibles */}
          {showDownloadOptions && (
            <div className="space-y-2 rounded-md border border-neutral-200 bg-white p-3 dark:border-neutral-700 dark:bg-neutral-800">
              <div className="text-xs font-semibold tracking-wide text-neutral-500 uppercase">
                Individual Files
              </div>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={handleDownloadBrewfile}
                  className="rounded bg-green-600 px-3 py-2 text-xs font-medium text-white hover:bg-green-500"
                >
                  Brewfile
                </button>
                <button
                  onClick={handleDownloadPostConfig}
                  className="rounded bg-orange-600 px-3 py-2 text-xs font-medium text-white hover:bg-orange-500"
                >
                  postConfig.sh
                </button>
                <button
                  onClick={handleDownloadCustomInstall}
                  className="rounded bg-purple-600 px-3 py-2 text-xs font-medium text-white hover:bg-purple-500"
                >
                  customInstall.sh
                </button>
                <button
                  onClick={handleDownloadMacSnap}
                  className="rounded bg-indigo-600 px-3 py-2 text-xs font-medium text-white hover:bg-indigo-500"
                >
                  macSnap.sh (Main Script)
                </button>
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

        <div className="pt-2">
          <div className="mb-2 text-xs tracking-wide text-neutral-500 uppercase">Selected apps</div>
          <div className="max-h-64 space-y-2 overflow-auto pr-2">
            {selectedList.map(p => (
              <div
                key={p.id}
                className="flex items-center justify-between rounded bg-neutral-900/40 px-2 py-1"
              >
                <div className="truncate text-sm" title={p.name}>
                  {p.name}
                </div>
                <button
                  className="rounded border border-neutral-700 px-2 py-0.5 text-xs hover:bg-neutral-800"
                  onClick={() => useSelectionStore.getState().toggle(p)}
                >
                  Remove
                </button>
              </div>
            ))}
            {selectedList.length === 0 && (
              <div className="text-neutral-500">Nothing selected yet</div>
            )}
          </div>
        </div>
      </div>
    </aside>
  );
};

export default SummaryPanel;
