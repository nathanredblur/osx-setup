import React from "react";
import { Home, SlidersHorizontal, Settings } from "lucide-react";

const NavItem: React.FC<{
  href: string;
  icon: React.ReactNode;
  label: string;
}> = ({ href, icon, label }) => (
  <a
    href={href}
    className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-neutral-800/70 text-neutral-200"
  >
    <span className="w-5 h-5">{icon}</span>
    <span className="text-sm font-medium">{label}</span>
  </a>
);

const SidebarNav: React.FC = () => {
  return (
    <aside className="w-56 shrink-0 h-full bg-neutral-900 text-neutral-100 flex flex-col border-r border-neutral-800">
      <div className="px-4 py-4 text-lg font-semibold">Mac Setup</div>
      <nav className="flex-1 px-2 space-y-1">
        <NavItem href="/" icon={<Home className="w-5 h-5" />} label="Apps" />
        <NavItem
          href="/tweeks"
          icon={<SlidersHorizontal className="w-5 h-5" />}
          label="Tweeks"
        />
        <NavItem
          href="/settings"
          icon={<Settings className="w-5 h-5" />}
          label="Settings"
        />
      </nav>
      <div className="px-4 py-3 text-xs text-neutral-400">v0.1.0</div>
    </aside>
  );
};

export default SidebarNav;
