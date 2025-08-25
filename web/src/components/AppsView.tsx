import AppGrid from '@/components/AppGrid';
import {ToastProvider} from '@/components/Toast';
import {DataProvider} from '@/context/DataContext';
import React from 'react';
import FiltersBar from './FiltersBar';
import SummaryPanel from './SummaryPanel';

const AppsView: React.FC = () => {
  return (
    <DataProvider>
      <ToastProvider>
        <div className="flex h-full">
          <div className="flex flex-1 flex-col overflow-hidden">
            <FiltersBar />
            <div className="flex flex-1 overflow-hidden">
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
