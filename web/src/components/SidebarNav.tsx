import {Home, Settings, SlidersHorizontal} from 'lucide-react';
import React from 'react';

const NavItem: React.FC<{
  href: string;
  icon: React.ReactNode;
  label: string;
}> = ({href, icon, label}) => (
  <a
    href={href}
    className="flex flex-col items-center gap-1 rounded-md px-2 py-3 text-neutral-800 hover:bg-neutral-400 dark:text-neutral-200 dark:hover:bg-neutral-800/70"
  >
    <span className="h-7 w-7">{icon}</span>
    <span className="text-[11px] font-medium">{label}</span>
  </a>
);

const SidebarNav: React.FC = () => {
  return (
    <aside className="flex h-full w-20 shrink-0 flex-col border-r border-neutral-200 bg-white text-neutral-900 dark:border-neutral-800 dark:bg-neutral-950 dark:text-neutral-100">
      <div className="px-2 py-4 text-center text-[11px] font-semibold">Mac</div>
      <nav className="flex-1 space-y-2 px-2">
        <NavItem href="/" icon={<Home className="h-5 w-5" />} label="Apps" />
        <NavItem href="/tweeks" icon={<SlidersHorizontal className="h-5 w-5" />} label="Tweeks" />
        <NavItem href="/settings" icon={<Settings className="h-5 w-5" />} label="Settings" />
      </nav>
      <div className="px-2 py-3 text-center text-[10px] text-neutral-500">v0.1.0</div>
    </aside>
  );
};

export default SidebarNav;
