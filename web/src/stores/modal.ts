import {create} from 'zustand';

interface ModalState {
  detailAppId: string | null;
  openAppDetail: (appId: string) => void;
  closeAppDetail: () => void;
}

export const useModalStore = create<ModalState>(set => ({
  detailAppId: null,
  openAppDetail: (appId: string) => set({detailAppId: appId}),
  closeAppDetail: () => set({detailAppId: null}),
}));
