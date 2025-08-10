import React, { useEffect, useState } from "react";

function usePersistedToggle(key: string, initial: boolean) {
  const [value, setValue] = useState<boolean>(() => {
    if (typeof window === "undefined") return initial;
    const raw = window.localStorage.getItem(key);
    return raw ? raw === "1" : initial;
  });
  useEffect(() => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(key, value ? "1" : "0");
    }
  }, [key, value]);
  return [value, setValue] as const;
}

const TweeksView: React.FC = () => {
  const [verbose, setVerbose] = usePersistedToggle("tweeks.verbose", false);
  const [skipInstalled, setSkipInstalled] = usePersistedToggle(
    "tweeks.skipInstalled",
    true
  );

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Tweeks</h1>
      <div className="space-y-4 max-w-2xl">
        <label className="flex items-center justify-between p-4 bg-neutral-100 dark:bg-neutral-800 rounded-md cursor-pointer">
          <span className="font-medium">Enable verbose install logs</span>
          <input
            type="checkbox"
            className="h-4 w-4"
            checked={verbose}
            onChange={(e) => setVerbose(e.target.checked)}
          />
        </label>
        <label className="flex items-center justify-between p-4 bg-neutral-100 dark:bg-neutral-800 rounded-md cursor-pointer">
          <span className="font-medium">Skip already installed apps</span>
          <input
            type="checkbox"
            className="h-4 w-4"
            checked={skipInstalled}
            onChange={(e) => setSkipInstalled(e.target.checked)}
          />
        </label>
      </div>
    </div>
  );
};

export default TweeksView;
