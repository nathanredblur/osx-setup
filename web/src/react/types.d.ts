export type InstallType = "brew" | "cask" | "mas";

export interface ProgramMeta {
  id: string;
  name: string;
  slug?: string;
  icon?: string;
  version?: string;
  url?: string;
  paid?: boolean;
  hasSettings?: boolean;
  type?: InstallType;
  tags?: string[];
  category?: string;
}
