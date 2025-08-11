import {Button} from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import * as Icons from 'lucide-react';
import React from 'react';

const iconComponentById: Record<string, any> = {
  Browsers: Icons.Globe,
  Cloud: Icons.Cloud,
  Communication: Icons.MessageSquare,
  'System Tweaks': Icons.Settings2,
  Security: Icons.Shield,
  Terminal: Icons.TerminalSquare,
  Utilities: Icons.Boxes,
  Development: Icons.Hammer,
  Media: Icons.Film,
  'Core Utilities': Icons.Grid2X2,
};

function renderIcon(id?: string) {
  const Comp = (id && iconComponentById[id]) || Icons.Grid2X2;
  return React.createElement(Comp as any, {className: 'w-4 h-4'});
}

export default function CategoryMenu({
  categories,
  value,
  onChange,
}: {
  categories: string[];
  value: string | null;
  onChange: (val: string | null) => void;
}) {
  const label = value || 'All Apps';
  const currentIcon = renderIcon(value?.toLowerCase().replaceAll(' ', '-'));

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="pr-3 pl-2">
          <span className="mr-2">{currentIcon}</span>
          {label}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem onSelect={() => onChange(null)}>
          {renderIcon('core-utilities')} <span>All Apps</span>
        </DropdownMenuItem>
        {categories.map(c => (
          <DropdownMenuItem key={c} onSelect={() => onChange(c)}>
            {renderIcon(c)} <span>{c}</span>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
