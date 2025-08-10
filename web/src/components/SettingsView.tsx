import React, { useEffect, useState } from "react";

const SettingsView: React.FC = () => {
  const [theme, setThemeState] = useState<"theme-light" | "dark" | "system">(
    "theme-light"
  );

  useEffect(() => {
    const isDarkMode = document.documentElement.classList.contains("dark");
    setThemeState(isDarkMode ? "dark" : "theme-light");
  }, []);

  React.useEffect(() => {
    const isDark =
      theme === "dark" ||
      (theme === "system" &&
        window.matchMedia("(prefers-color-scheme: dark)").matches);
    document.documentElement.classList[isDark ? "add" : "remove"]("dark");
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
            onClick={() => setThemeState("system")}
          >
            System
          </button>
          <button
            className={`px-3 py-2 rounded-md bg-neutral-200 dark:bg-neutral-700 ${
              theme === "theme-light" ? "ring-2 ring-blue-500" : ""
            }`}
            onClick={() => setThemeState("theme-light")}
          >
            Light
          </button>
          <button
            className={`px-3 py-2 rounded-md bg-neutral-200 dark:bg-neutral-700 ${
              theme === "dark" ? "ring-2 ring-blue-500" : ""
            }`}
            onClick={() => setThemeState("dark")}
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
