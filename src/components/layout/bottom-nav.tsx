import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/auth-context";
import { ThemeToggle } from "../theme-toggle";
import {
  User,
  Settings,
  LogOut
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function BottomNav() {
  const location = useLocation();
  const { logout } = useAuth();

  const navItems = [
    {
      name: "Profile",
      href: "/profile",
      icon: <User className="h-5 w-5" />,
    },
    {
      name: "Settings",
      href: "/settings",
      icon: <Settings className="h-5 w-5" />,
    },
  ];

  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-background border-t p-2 flex items-center justify-between">
      {navItems.map((item) => (
        <Link key={item.href} to={item.href} className="flex-1">
          <Button
            variant={location.pathname === item.href ? "secondary" : "ghost"}
            className={cn(
              "w-full flex flex-col items-center py-1 h-auto",
              location.pathname === item.href
                ? "bg-secondary text-secondary-foreground"
                : "hover:bg-secondary/50"
            )}
          >
            {item.icon}
            <span className="text-xs mt-1">{item.name}</span>
          </Button>
        </Link>
      ))}
      
      <div className="flex-1 flex justify-center">
        <ThemeToggle />
      </div>
      
      <div className="flex-1 flex justify-center">
        <Button variant="ghost" size="icon" onClick={logout} className="flex flex-col items-center py-1 h-auto">
          <LogOut className="h-5 w-5" />
          <span className="text-xs mt-1">Logout</span>
        </Button>
      </div>
    </div>
  );
}