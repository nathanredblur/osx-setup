export type InstallType = "brew" | "cask" | "mas";

export interface ProgramMeta {
  id: string;
  name: string;
  slug?: string;
  /** brew/cask token when available */
  token?: string;
  /** Mac App Store numeric id when available */
  masId?: string;
  icon?: string;
  version?: string;
  url?: string;
  description?: string;
  paid?: boolean;
  hasSettings?: boolean;
  type?: InstallType;
  tags?: string[];
  category?: string;
  notes?: string;
  dependencies?: string[];
  installScript?: string | null;
  validateScript?: string | null;
  configureScript?: string | null;
  uninstallScript?: string | null;
}
