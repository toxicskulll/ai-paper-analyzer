import { useState, useEffect } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "@/context/auth-context";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";
import { Badge } from "@/components/ui/badge";
import {
  LogOut,
  Users,
  KeyRound,
  BarChart3,
  Menu,
  X,
  Activity,
  Settings,
  Shield,
  UserCheck,
  Database,
  Server,
  AlertTriangle
} from "lucide-react";

export default function AdminLayout() {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobile, setIsMobile] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Check if user is admin, redirect if not
  useEffect(() => {
    if (user && !isAdmin) {
      navigate("/dashboard");
    }
  }, [user, isAdmin, navigate]);

  // Handle responsive sidebar
  useEffect(() => {
    const checkSize = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkSize();
    window.addEventListener("resize", checkSize);
    return () => window.removeEventListener("resize", checkSize);
  }, []);

  // Remove redundant navItems for dashboard sections
  const navItems = [
    {
      icon: <BarChart3 className="h-5 w-5 mr-3 transition-transform duration-200 group-hover:scale-110" />, 
      name: "Dashboard Home", 
      path: "/admin/dashboard",
    },
    {
      icon: <Users className="h-5 w-5 mr-3 transition-transform duration-200 group-hover:scale-110" />, 
      name: "Profile", 
      path: "/admin/profile",
    },
  ];

  const quickActions = [
    {
      icon: <UserCheck className="h-4 w-4" />,
      name: "New User",
      action: () => navigate("/admin/users")
    },
    {
      icon: <KeyRound className="h-4 w-4" />,
      name: "Generate License",
      action: () => navigate("/admin/licenses")
    },
    {
      icon: <Database className="h-4 w-4" />,
      name: "Backup System",
      action: () => navigate("/admin/settings")
    }
  ];

  const isActivePath = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + "/");
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Admin Sidebar */}
      <div
        className={`${
          isMobile
            ? `fixed inset-y-0 left-0 z-50 transform ${
                sidebarOpen ? "translate-x-0" : "-translate-x-full"
              } transition-transform duration-300 ease-in-out`
            : "relative"
        } bg-card border-r border-border w-64 flex flex-col transition-all duration-300`}
      >
        {isMobile && (
          <Button 
            variant="ghost" 
            size="icon"
            className="absolute right-2 top-2 text-foreground hover:bg-secondary"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-5 w-5" />
          </Button>
        )}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <span className="font-bold text-xl bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            Admin Panel
          </span>
        </div>
        {/* User info */}
        <div className="border-b border-border p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-primary/10 text-primary flex items-center justify-center">
              <span className="font-medium text-sm">{user?.name?.charAt(0)}</span>
            </div>
            <div>
              <p className="font-medium text-sm">{user?.name}</p>
              <p className="text-xs text-muted-foreground">{user?.email}</p>
            </div>
          </div>
        </div>
        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-1">
          {navItems.map((item) => (
            <Button
              key={item.path}
              variant={location.pathname === item.path ? "secondary" : "ghost"}
              className={`w-full justify-start group transition-all duration-200 ${location.pathname === item.path ? "bg-secondary text-secondary-foreground" : "hover:bg-secondary/50"}`}
              onClick={() => {
                navigate(item.path);
                if (isMobile) setSidebarOpen(false);
              }}
            >
              {item.icon}
              {item.name}
            </Button>
          ))}
        </nav>
        {/* Footer - Desktop only */}
        <div className="border-t border-border p-4 space-y-2 hidden md:block mt-auto">
          <div className="flex items-center justify-between">
            <ThemeToggle />
            <Button variant="ghost" size="icon" onClick={logout}>
              <LogOut className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile overlay */}
      {isMobile && sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}

      {/* Main content area */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top admin bar */}
        <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-4 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="flex items-center">
            {isMobile && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSidebarOpen(true)}
              >
                <Menu className="h-5 w-5" />
              </Button>
            )}
            <div className="ml-4">
              <h1 className="text-xl font-semibold flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" />
                Admin Control Panel
              </h1>
              <p className="text-sm text-muted-foreground">
                System Administration
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm text-muted-foreground">System Online</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs">
                <Shield className="h-3 w-3 mr-1" />
                Admin
              </Badge>
              <span className="text-sm font-medium">{user?.name}</span>
            </div>
          </div>
        </header>
        
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}