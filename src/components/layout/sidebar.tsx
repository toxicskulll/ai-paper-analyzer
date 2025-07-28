import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useAuth } from "@/context/auth-context";
import { ThemeToggle } from "../theme-toggle";
import {
  LayoutDashboard,
  Search,
  Library,
  FileText,
  Clock,
  Code,
  LogOut,
  X,
  InfoIcon
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  onClose?: () => void;
}

export default function Sidebar({ onClose }: SidebarProps) {
  const location = useLocation();
  const { user, logout } = useAuth();

  const navItems = [
    {
      name: "Dashboard",
      href: "/dashboard",
      icon: <LayoutDashboard className="mr-2 h-5 w-5" />,
    },
    {
      name: "Paper Scraper",
      href: "/scraper",
      icon: <Search className="mr-2 h-5 w-5" />,
    },
    {
      name: "Paper Library",
      href: "/library",
      icon: <Library className="mr-2 h-5 w-5" />,
    },
    {
      name: "Analyzer",
      href: "/analyzer",
      icon: <FileText className="mr-2 h-5 w-5" />,
    },
    {
      name: "Activity Log",
      href: "/activity",
      icon: <Clock className="mr-2 h-5 w-5" />,
    },
    {
      name: "About Developer",
      href: "/about-developer",
      icon: <InfoIcon className="mr-2 h-5 w-5" />,
    },
  ];

  return (
    <div className="flex flex-col h-full w-64 bg-card border-r border-border">
      <div className="flex items-center justify-between p-4">
        <Link to="/" className="flex items-center space-x-2">
          <span className="font-bold text-xl bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            ResearchAI Pro
          </span>
        </Link>
        
        {/* Mobile close button */}
        <Button
          variant="ghost"
          size="icon"
          onClick={onClose}
          className="md:hidden"
        >
          <X className="h-5 w-5" />
        </Button>
      </div>

      {/* User info */}
      <div className="border-t border-b border-border p-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-primary/10 text-primary flex items-center justify-center">
            <span className="font-medium text-sm">{user?.name.charAt(0)}</span>
          </div>
          <div>
            <p className="font-medium text-sm">{user?.name}</p>
            <p className="text-xs text-muted-foreground">{user?.email}</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <ScrollArea className="flex-1 py-2">
        <nav className="px-2 space-y-1">
          {navItems.map((item) => (
            <Link key={item.href} to={item.href}>
              <Button
                variant={location.pathname === item.href ? "secondary" : "ghost"}
                className={cn(
                  "w-full justify-start",
                  location.pathname === item.href
                    ? "bg-secondary text-secondary-foreground"
                    : "hover:bg-secondary/50"
                )}
              >
                {item.icon}
                {item.name}
              </Button>
            </Link>
          ))}
        </nav>
      </ScrollArea>

      {/* Footer - Desktop only */}
      <div className="border-t border-border p-4 space-y-2 hidden md:block">
        <div className="flex items-center justify-between">
          <ThemeToggle />
          <Button variant="ghost" size="icon" onClick={logout}>
            <LogOut className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  );
}