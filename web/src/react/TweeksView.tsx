import React from "react";

const TweeksView: React.FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Tweeks</h1>
      <div className="space-y-4 max-w-2xl">
        <div className="flex items-center justify-between p-4 bg-neutral-100 dark:bg-neutral-800 rounded-md">
          <span className="font-medium">Enable verbose install logs</span>
          <input type="checkbox" className="h-4 w-4" />
        </div>
        <div className="flex items-center justify-between p-4 bg-neutral-100 dark:bg-neutral-800 rounded-md">
          <span className="font-medium">Skip already installed apps</span>
          <input type="checkbox" className="h-4 w-4" />
        </div>
      </div>
    </div>
  );
};

export default TweeksView;
