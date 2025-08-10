import React from "react";
import FiltersBar from "./FiltersBar";
import SummaryPanel from "./SummaryPanel";
import AppGrid from "@/components/AppGrid";
import { DataProvider } from "@/context/DataContext";
import { ToastProvider } from "@/components/Toast";

const AppsView: React.FC = () => {
  return (
    <DataProvider>
      <ToastProvider>
        <div className="h-full flex">
          <div className="flex-1 flex flex-col overflow-hidden">
            <FiltersBar />
            <div className="flex-1 overflow-hidden flex">
              <div className="flex-1 overflow-auto">
                <AppGrid />
              </div>
              <SummaryPanel />
            </div>
          </div>
        </div>
      </ToastProvider>
    </DataProvider>
  );
};

export default AppsView;
