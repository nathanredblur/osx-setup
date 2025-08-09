import React from "react";
import FiltersBar from "./FiltersBar";
import SummaryPanel from "./SummaryPanel";
import AppGrid from "./grid/AppGrid";
import { DataProvider } from "./data/DataContext";

const AppsView: React.FC = () => {
  return (
    <DataProvider>
      <div className="h-full flex">
        <SummaryPanel />
        <div className="flex-1 flex flex-col overflow-hidden">
          <FiltersBar />
          <div className="flex-1 overflow-auto">
            <AppGrid />
          </div>
        </div>
      </div>
    </DataProvider>
  );
};

export default AppsView;
