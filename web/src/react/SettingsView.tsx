import React, { useEffect, useState } from "react";

function applyTheme(theme: "system" | "light" | "dark") {
  if (theme === "system") {
    document.documentElement.classList.toggle(
      "dark",
      window.matchMedia("(prefers-color-scheme: dark)").matches
    );
  } else {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }
}

const SettingsView: React.FC = () => {
  const [theme, setTheme] = useState<"system" | "light" | "dark">("system");

  useEffect(() => {
    // read persisted theme on mount (client only)
    if (typeof window !== "undefined") {
      const saved =
        (window.localStorage.getItem("pref.theme") as any) || "system";
      setTheme(saved);
      applyTheme(saved);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (typeof window !== "undefined") {
      applyTheme(theme);
      window.localStorage.setItem("pref.theme", theme);
    }
  }, [theme]);

  return (
    <div className="p-6 space-y-6 max-w-3xl">
      <h1 className="text-2xl font-semibold">Settings</h1>
      <section className="space-y-3">
        <h2 className="text-lg font-medium">Theme</h2>
        <div className="flex gap-3">
          <button
            className={`px-3 py-2 rounded-md bg-neutral-200 dark:bg-neutral-700 ${
              theme === "system" ? "ring-2 ring-blue-500" : ""
            }`}
            onClick={() => setTheme("system")}
          >
            System
          </button>
          <button
            className={`px-3 py-2 rounded-md bg-neutral-200 dark:bg-neutral-700 ${
              theme === "light" ? "ring-2 ring-blue-500" : ""
            }`}
            onClick={() => setTheme("light")}
          >
            Light
          </button>
          <button
            className={`px-3 py-2 rounded-md bg-neutral-200 dark:bg-neutral-700 ${
              theme === "dark" ? "ring-2 ring-blue-500" : ""
            }`}
            onClick={() => setTheme("dark")}
          >
            Dark
          </button>
        </div>
      </section>
      <section className="space-y-3">
        <h2 className="text-lg font-medium">Cache & Catalog</h2>
        <div className="flex gap-3">
          <button className="px-3 py-2 rounded-md bg-neutral-200 dark:bg-neutral-700">
            Clear cache
          </button>
          <button className="px-3 py-2 rounded-md bg-neutral-200 dark:bg-neutral-700">
            Reload catalog
          </button>
        </div>
      </section>
    </div>
  );
};

export default SettingsView;
