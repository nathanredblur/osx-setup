import React from "react";

const SettingsView: React.FC = () => {
  return (
    <div className="p-6 space-y-6 max-w-3xl">
      <h1 className="text-2xl font-semibold">Settings</h1>
      <section className="space-y-3">
        <h2 className="text-lg font-medium">Theme</h2>
        <div className="flex gap-3">
          <button className="px-3 py-2 rounded-md bg-neutral-200 dark:bg-neutral-700">
            System
          </button>
          <button className="px-3 py-2 rounded-md bg-neutral-200 dark:bg-neutral-700">
            Light
          </button>
          <button className="px-3 py-2 rounded-md bg-neutral-200 dark:bg-neutral-700">
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
