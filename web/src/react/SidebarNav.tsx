import React from "react";
import { Home, SlidersHorizontal, Settings } from "lucide-react";

const NavItem: React.FC<{
  href: string;
  icon: React.ReactNode;
  label: string;
}> = ({ href, icon, label }) => (
  <a
    href={href}
    className="flex flex-col items-center gap-1 px-2 py-3 rounded-md hover:bg-neutral-800/70 text-neutral-300"
  >
    <span className="w-7 h-7">{icon}</span>
    <span className="text-[11px] font-medium">{label}</span>
  </a>
);

const SidebarNav: React.FC = () => {
  return (
    <aside className="w-20 shrink-0 h-full bg-neutral-950 text-neutral-100 flex flex-col border-r border-neutral-800">
      <div className="px-2 py-4 text-center text-[11px] font-semibold">Mac</div>
      <nav className="flex-1 px-2 space-y-2">
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
      <div className="px-2 py-3 text-[10px] text-neutral-500 text-center">
        v0.1.0
      </div>
    </aside>
  );
};

export default SidebarNav;
