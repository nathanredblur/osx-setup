import {useToast} from '@/components/Toast';
import {singleInstallCommand} from '@/lib/bundle';
import type {ProgramMeta} from '@/types/data.d.ts';
import React, {useEffect, useState} from 'react';

interface BrewApiData {
  name: string[];
  desc: string;
  homepage: string;
  version: string;
  url: string;
  deprecated?: boolean;
  deprecation_reason?: string;
  caveats?: string;
}

type Props = {
  program: ProgramMeta | null;
  onClose: () => void;
  onToggle: () => void;
  selected: boolean;
};

const AppDetail: React.FC<Props> = ({program, onClose, onToggle, selected}) => {
  const toast = useToast();
  const [brewData, setBrewData] = useState<BrewApiData | null>(null);
  const [faviconUrl, setFaviconUrl] = useState<string | null>(null);
  const [loadingBrew, setLoadingBrew] = useState(false);
  const [loadingFavicon, setLoadingFavicon] = useState(false);

  // Extract bundle name from bundle string (e.g., 'cask "google-chrome"' -> 'google-chrome')
  const extractBundleName = (bundle: string): string | null => {
    const match = bundle.match(/^(brew|cask|mas)\s+"([^"]+)"/);
    return match ? match[2] : null;
  };

  // Fetch Homebrew API data
  const fetchBrewData = async (bundleName: string, type: string) => {
    if (type !== 'cask' && type !== 'brew') return;

    setLoadingBrew(true);
    try {
      const endpoint = type === 'cask' ? 'cask' : 'formula';
      const response = await fetch(`https://formulae.brew.sh/api/${endpoint}/${bundleName}.json`);
      if (response.ok) {
        const data = await response.json();
        setBrewData(data);

        // Try to get favicon from homepage
        if (data.homepage) {
          fetchFavicon(data.homepage);
        }
      }
    } catch (error) {
      console.warn('Failed to fetch Homebrew data:', error);
    } finally {
      setLoadingBrew(false);
    }
  };

  // Fetch favicon from homepage
  const fetchFavicon = async (homepage: string) => {
    setLoadingFavicon(true);
    try {
      const url = new URL(homepage);
      const faviconUrl = `${url.protocol}//${url.host}/favicon.ico`;

      // Test if favicon exists
      const response = await fetch(faviconUrl, {method: 'HEAD'});
      if (response.ok) {
        setFaviconUrl(faviconUrl);
      }
    } catch (error) {
      console.warn('Failed to fetch favicon:', error);
    } finally {
      setLoadingFavicon(false);
    }
  };

  // Effect to fetch data when program changes
  useEffect(() => {
    if (program?.bundle && (program.type === 'cask' || program.type === 'brew')) {
      const bundleName = extractBundleName(program.bundle);
      if (bundleName) {
        fetchBrewData(bundleName, program.type);
      }
    } else {
      setBrewData(null);
      setFaviconUrl(null);
    }
  }, [program]);

  if (!program) return null;
  return (
    <div className="fixed inset-0 z-50 flex">
      <div className="flex-1 bg-black/40" onClick={onClose} />
      <div className="h-full w-[420px] max-w-full overflow-y-auto border-l border-neutral-200 bg-white p-6 dark:border-neutral-800 dark:bg-neutral-900">
        <div className="flex items-center gap-3">
          <div className="relative h-12 w-12">
            <img
              src={faviconUrl || program.image || '/icons/default-app.svg'}
              alt="icon"
              className="h-12 w-12 rounded"
              onError={e => {
                // Fallback to program image or default if favicon fails
                const target = e.target as HTMLImageElement;
                if (target.src === faviconUrl) {
                  target.src = program.image || '/icons/default-app.svg';
                }
              }}
            />
            {loadingFavicon && (
              <div className="absolute inset-0 flex items-center justify-center rounded bg-neutral-100 dark:bg-neutral-800">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-neutral-300 border-t-neutral-600"></div>
              </div>
            )}
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
