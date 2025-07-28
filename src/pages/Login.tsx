import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/context/auth-context";
import { ThemeToggle } from "@/components/theme-toggle";
import { Github, Chrome } from "lucide-react";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [licenseKey, setLicenseKey] = useState("");
  const [adminSecretKey, setAdminSecretKey] = useState("");
  const [isAdminMode, setIsAdminMode] = useState(false);
  const { login, adminLogin, socialLogin, adminSocialLogin, isLoading } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isAdminMode) {
      if (!adminSecretKey.trim()) {
        toast.error("Admin Secret Key is required");
        return;
      }
      await adminLogin(email, password, adminSecretKey);
    } else {
      if (!licenseKey.trim()) {
        toast.error("License Key is required");
        return;
      }
      await login(email, password, licenseKey);
    }
  };

  const handleSocialLogin = async (provider: string) => {
    if (isAdminMode) {
      if (!adminSecretKey.trim()) {
        toast.error("Admin Secret Key is required for admin login");
        return;
      }
      await adminSocialLogin(provider, adminSecretKey);
    } else {
      if (!licenseKey.trim()) {
        toast.error("License Key is required");
        return;
      }
      await socialLogin(provider, licenseKey);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>

      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            AI Research Paper Analyzer Pro
          </h1>
          <p className="mt-2 text-muted-foreground">
            Your comprehensive academic research management platform
          </p>
          {isAdminMode && (
            <Badge variant="destructive" className="mt-2">
              Admin Access
            </Badge>
          )}
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  {isAdminMode ? "Admin Sign In" : "Sign In"}
                  {isAdminMode && <Badge variant="outline">Admin</Badge>}
                </CardTitle>
                <CardDescription>
                  {isAdminMode 
                    ? "Enter your admin credentials and secret key to access the system" 
                    : "Enter your credentials and license key to access your account"
                  }
                </CardDescription>
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => {
                  setIsAdminMode(!isAdminMode);
                  setEmail("");
                  setPassword("");
                  setLicenseKey("");
                  setAdminSecretKey("");
                }}
                type="button"
              >
                {isAdminMode ? "User Login" : "Admin Login"}
              </Button>
            </div>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              {/* Demo Credentials */}
              <div className="p-4 bg-muted/50 rounded-lg border">
                <h4 className="font-medium text-sm mb-2">Demo Credentials:</h4>
                {isAdminMode ? (
                  <div className="space-y-1 text-xs">
                    <p><strong>Admin Email:</strong> admin@example.com</p>
                    <p><strong>Admin Password:</strong> admin123</p>
                    <p><strong>Admin Secret Key:</strong> ADMIN_SECRET_2024</p>
                  </div>
                ) : (
                  <div className="space-y-1 text-xs">
                    <p><strong>User Email:</strong> user@example.com</p>
                    <p><strong>User Password:</strong> user123</p>
                    <p><strong>License Key:</strong> LICENSE-ABC123-XYZ789</p>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password">Password</Label>
                  <Link
                    to="#"
                    className="text-xs text-primary hover:underline"
                  >
                    Forgot password?
                  </Link>
                </div>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              
              {isAdminMode ? (
                <div className="space-y-2">
                  <Label htmlFor="adminSecretKey">
                    Admin Secret Key <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="adminSecretKey"
                    type="password"
                    placeholder="Enter admin secret key"
                    value={adminSecretKey}
                    onChange={(e) => setAdminSecretKey(e.target.value)}
                    required
                  />
                  <p className="text-xs text-muted-foreground">
                    Contact the platform owner for secure admin access
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  <Label htmlFor="licenseKey">
                    License Key <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="licenseKey"
                    type="text"
                    placeholder="Enter your license key"
                    value={licenseKey}
                    onChange={(e) => setLicenseKey(e.target.value)}
                    required
                  />
                  <p className="text-xs text-muted-foreground">
                    Contact support for license key assistance
                  </p>
                </div>
              )}

              <Button 
                type="submit" 
                className="w-full" 
                disabled={isLoading}
              >
                {isLoading ? "Signing in..." : (isAdminMode ? "Admin Sign In" : "Sign In")}
              </Button>
            </CardContent>
          </form>

          <CardFooter className="flex flex-col space-y-4">
            <div className="relative w-full">
              <div className="absolute inset-0 flex items-center">
                <Separator className="w-full" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">
                  Or continue with
                </span>
              </div>
            </div>

            <div className="flex gap-2 w-full">
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => handleSocialLogin("google")}
                disabled={isLoading}
              >
                <Chrome className="mr-2 h-4 w-4" />
                Google
              </Button>
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => handleSocialLogin("github")}
                disabled={isLoading}
              >
                <Github className="mr-2 h-4 w-4" />
                GitHub
              </Button>
            </div>

            <div className="text-center text-sm">
              <span className="text-muted-foreground">
                {isAdminMode ? "Need admin access?" : "Don't have an account?"}
              </span>{" "}
              <Link
                to={isAdminMode ? "/admin-register" : "/register"}
                className="text-primary hover:underline font-medium"
              >
                {isAdminMode ? "Contact platform owner" : "Sign up"}
              </Link>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}