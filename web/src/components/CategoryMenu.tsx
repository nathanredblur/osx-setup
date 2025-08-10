import React from "react";
import * as Icons from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

type Category = { id: string; name: string };

const iconComponentById: Record<string, any> = {
  browsers: Icons.Globe,
  cloud: Icons.Cloud,
  communication: Icons.MessageSquare,
  "system-tweaks": Icons.Settings2,
  security: Icons.Shield,
  terminal: Icons.TerminalSquare,
  utilities: Icons.Boxes,
  development: Icons.Hammer,
  media: Icons.Film,
  "core-utilities": Icons.Grid2X2,
};

function renderIcon(id?: string) {
  const Comp = (id && iconComponentById[id]) || Icons.Grid2X2;
  return React.createElement(Comp as any, { className: "w-4 h-4" });
}

export default function CategoryMenu({
  categories,
  value,
  onChange,
}: {
  categories: Category[];
  value: string | null;
  onChange: (val: string | null) => void;
}) {
  const label = value || "All Apps";
  const currentIcon = renderIcon(value?.toLowerCase().replaceAll(" ", "-"));

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="pl-2 pr-3">
          <span className="mr-2">{currentIcon}</span>
          {label}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem onSelect={() => onChange(null)}>
          {renderIcon("core-utilities")} <span>All Apps</span>
        </DropdownMenuItem>
        {categories.map((c) => (
          <DropdownMenuItem key={c.id} onSelect={() => onChange(c.name)}>
            {renderIcon(c.id)} <span>{c.name}</span>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
