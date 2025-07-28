import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { toast } from "sonner";

interface User {
  id: string;
  name: string;
  email: string;
  role: "user" | "admin";
  licenseKey?: string;
  status: "active" | "suspended";
  authMethod: "email" | "google" | "github";
  createdAt: string;
  lastLogin: string;
}

interface AdminUser extends User {
  role: "admin";
  permissions: string[];
  secretKey: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string, licenseKey: string) => Promise<void>;
  socialLogin: (provider: string, licenseKey: string) => Promise<void>;
  register: (name: string, email: string, password: string, isAdmin: boolean, adminKey?: string) => Promise<void>;
  adminLogin: (email: string, password: string, secretKey: string) => Promise<void>;
  adminSocialLogin: (provider: string, secretKey: string) => Promise<void>;
  adminRegister: (name: string, email: string, password: string, secretKey: string) => Promise<void>;
  logout: () => void;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const navigate = useNavigate();
  const location = useLocation();

  // Check if user is authenticated
  useEffect(() => {
    const checkAuth = () => {
      const storedUser = localStorage.getItem("auth-user");
      if (storedUser) {
        setUser(JSON.parse(storedUser));
      }
      setIsLoading(false);
    };
    
    checkAuth();
  }, []);

  // Protected routes logic
  useEffect(() => {
    if (!isLoading) {
      const publicPaths = ["/login", "/register"];
      const isPublicPath = publicPaths.includes(location.pathname);
      
      if (!user && !isPublicPath) {
        navigate("/login", { replace: true });
      } else if (user && isPublicPath) {
        // Redirect admin users to admin dashboard, regular users to user dashboard
        if (user.role === "admin") {
          navigate("/admin/dashboard", { replace: true });
        } else {
          navigate("/dashboard", { replace: true });
        }
      }
    }
  }, [user, isLoading, navigate, location.pathname]);

  // Mock valid license keys
  const validLicenseKeys = ["LICENSE-ABC123-XYZ789", "LICENSE-123", "LICENSE-456", "LICENSE-789"];
  
  // Mock admin secret keys
  const validAdminSecretKeys = ["ADMIN_SECRET_2024", "ADMIN-SECRET-2024", "SUPER-ADMIN-KEY", "PLATFORM-OWNER-KEY"];
  
  // Mock login function with license key validation
  const login = async (email: string, password: string, licenseKey: string) => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // First validate license key
      if (!validLicenseKeys.includes(licenseKey)) {
        toast.error("Invalid license key: please contact the developer for sign-in assistance.");
        setIsLoading(false);
        return;
      }
      
      // Then validate credentials
      if (email === "user@example.com" && password === "user123") {
        const mockUser: User = {
          id: "user-1",
          name: "Demo User",
          email: "user@example.com",
          role: "user",
          licenseKey: licenseKey,
          status: "active",
          authMethod: "email",
          createdAt: "2024-01-01T00:00:00Z",
          lastLogin: new Date().toISOString()
        };
        
        localStorage.setItem("auth-user", JSON.stringify(mockUser));
        setUser(mockUser);
        toast.success("Successfully logged in!");
        navigate("/dashboard");
      } else {
        toast.error("Invalid email or password");
      }
    } catch (error) {
      toast.error("Login failed. Please try again.");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  // Enhanced admin login with secret key validation
  const adminLogin = async (email: string, password: string, secretKey: string) => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Validate admin secret key first
      if (!validAdminSecretKeys.includes(secretKey)) {
        toast.error("Invalid secret key. Contact the platform owner for secure access.");
        setIsLoading(false);
        return;
      }
      
      // Then validate admin credentials
      if (email === "admin@example.com" && password === "admin123") {
        const mockAdminUser: AdminUser = {
          id: "admin-1",
          name: "Admin User",
          email: "admin@example.com",
          role: "admin",
          status: "active",
          authMethod: "email",
          createdAt: "2024-01-01T00:00:00Z",
          lastLogin: new Date().toISOString(),
          secretKey: secretKey,
          permissions: ["user_management", "license_management", "system_settings", "audit_logs", "analytics"]
        };
        
        localStorage.setItem("auth-user", JSON.stringify(mockAdminUser));
        setUser(mockAdminUser);
        toast.success("Admin login successful!");
        navigate("/admin/dashboard");
      } else {
        toast.error("Invalid admin credentials");
      }
    } catch (error) {
      toast.error("Admin login failed. Please try again.");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  // Admin social login with secret key validation
  const adminSocialLogin = async (provider: string, secretKey: string) => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Validate admin secret key
      if (!validAdminSecretKeys.includes(secretKey)) {
        toast.error("Invalid secret key. Contact the platform owner for secure access.");
        setIsLoading(false);
        return;
      }
      
      // Mock successful social login for admin
      const mockAdminUser: AdminUser = {
        id: "admin-2",
        name: "Admin via " + provider,
        email: `admin@${provider}.com`,
        role: "admin",
        status: "active",
        authMethod: provider as "google" | "github",
        createdAt: "2024-01-01T00:00:00Z",
        lastLogin: new Date().toISOString(),
        secretKey: secretKey,
        permissions: ["user_management", "license_management", "system_settings", "audit_logs", "analytics"]
      };
      
      localStorage.setItem("auth-user", JSON.stringify(mockAdminUser));
      setUser(mockAdminUser);
      toast.success(`Admin login via ${provider} successful!`);
      navigate("/admin/dashboard");
    } catch (error) {
      toast.error(`Admin login via ${provider} failed. Please try again.`);
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  // Enhanced social login for regular users
  const socialLogin = async (provider: string, licenseKey: string) => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Validate license key
      if (!validLicenseKeys.includes(licenseKey)) {
        toast.error("Invalid license key: please contact the developer for sign-in assistance.");
        setIsLoading(false);
        return;
      }
      
      // Mock successful social login
      const mockUser: User = {
        id: "user-2",
        name: `User via ${provider}`,
        email: `user@${provider}.com`,
        role: "user",
        licenseKey: licenseKey,
        status: "active",
        authMethod: provider as "google" | "github",
        createdAt: "2024-01-01T00:00:00Z",
        lastLogin: new Date().toISOString()
      };
      
      localStorage.setItem("auth-user", JSON.stringify(mockUser));
      setUser(mockUser);
      toast.success(`Login via ${provider} successful!`);
      navigate("/dashboard");
    } catch (error) {
      toast.error(`Login via ${provider} failed. Please try again.`);
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  // Enhanced register function with admin support
  const register = async (name: string, email: string, password: string, isAdmin: boolean = false, adminKey?: string) => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (isAdmin) {
        // Validate admin secret key for admin registration
        if (!adminKey || !validAdminSecretKeys.includes(adminKey)) {
          toast.error("Invalid admin secret key. Contact the platform owner for admin access.");
          setIsLoading(false);
          return;
        }
        
        const mockAdminUser: AdminUser = {
          id: `admin-${Date.now()}`,
          name: name,
          email: email,
          role: "admin",
          status: "active",
          authMethod: "email",
          createdAt: new Date().toISOString(),
          lastLogin: new Date().toISOString(),
          secretKey: adminKey,
          permissions: ["user_management", "license_management", "system_settings", "audit_logs", "analytics"]
        };
        
        localStorage.setItem("auth-user", JSON.stringify(mockAdminUser));
        setUser(mockAdminUser);
        toast.success("Admin account created successfully!");
        navigate("/admin/dashboard");
      } else {
        // Regular user registration (requires license key)
        const mockUser: User = {
          id: `user-${Date.now()}`,
          name: name,
          email: email,
          role: "user",
          status: "active",
          authMethod: "email",
          createdAt: new Date().toISOString(),
          lastLogin: new Date().toISOString()
        };
        
        localStorage.setItem("auth-user", JSON.stringify(mockUser));
        setUser(mockUser);
        toast.success("Account created successfully! Please contact support for license key activation.");
        navigate("/dashboard");
      }
    } catch (error) {
      toast.error("Registration failed. Please try again.");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  // Admin registration function
  const adminRegister = async (name: string, email: string, password: string, secretKey: string) => {
    return register(name, email, password, true, secretKey);
  };

  const logout = () => {
    localStorage.removeItem("auth-user");
    setUser(null);
    toast.success("Logged out successfully");
    navigate("/login");
  };

  const isAdmin = user?.role === "admin";

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        socialLogin,
        register,
        adminLogin,
        adminSocialLogin,
        adminRegister,
        logout,
        isAdmin,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};