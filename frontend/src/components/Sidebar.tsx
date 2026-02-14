import { NavLink } from "react-router-dom";
import {
  Factory,
  Boxes,
  TrendingUp,
  Brain,
  Truck,
  Handshake,
} from "lucide-react";
import clsx from "clsx";

interface NavItem {
  to: string;
  label: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
}

const navItems: NavItem[] = [
  { to: "/fabric", label: "Fabric", icon: Factory },
  { to: "/frameworks", label: "Frameworks", icon: Boxes },
  { to: "/sales", label: "Sales", icon: TrendingUp },
  { to: "/intelligence", label: "Intelligence", icon: Brain },
  { to: "/deploy", label: "Deploy", icon: Truck },
  { to: "/partners", label: "Partners", icon: Handshake },
];

export default function Sidebar() {
  return (
    <aside className="w-60 h-full bg-surface border-r border-border flex flex-col">
      <div className="px-5 pt-6 pb-4">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-8 h-8 rounded-lg bg-eco-600 flex items-center justify-center">
            <span className="text-white text-sm font-bold">EC</span>
          </div>
          <div>
            <div className="text-sm font-semibold text-text-heading leading-tight">
              EcoContainer
            </div>
            <div className="text-[10px] text-text-tertiary leading-tight">
              Planta Smart Homes
            </div>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 space-y-0.5">
        <div className="px-2 pb-2 pt-1">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-text-tertiary">
            Modules
          </span>
        </div>
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-eco-50 text-eco-700"
                  : "text-text-secondary hover:text-text-primary hover:bg-surface-tertiary",
              )
            }
          >
            {({ isActive }) => (
              <>
                <item.icon
                  size={18}
                  className={clsx(
                    "flex-shrink-0 transition-colors",
                    isActive ? "text-eco-600" : "text-text-tertiary",
                  )}
                />
                <span>{item.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="px-5 py-4 border-t border-border">
        <div className="text-[10px] text-text-tertiary">
          OS + Brain Platform v1.0
        </div>
      </div>
    </aside>
  );
}
