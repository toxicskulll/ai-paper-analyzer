import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
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

export default function Register() {
  const location = useLocation();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [licenseKey, setLicenseKey] = useState("");
  const [adminSecretKey, setAdminSecretKey] = useState("");
  const [isAdminMode, setIsAdminMode] = useState(location.pathname === "/admin-register");
  const { register, adminRegister, isLoading } = useAuth();

  // Update admin mode when route changes
  useEffect(() => {
    setIsAdminMode(location.pathname === "/admin-register");
  }, [location.pathname]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    if (password.length < 8) {
      toast.error("Password must be at least 8 characters long");
      return;
    }

    if (isAdminMode) {
      if (!adminSecretKey.trim()) {
        toast.error("Admin Secret Key is required");
        return;
      }
      await adminRegister(name, email, password, adminSecretKey);
    } else {
      await register(name, email, password, false);
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
            Create your account to get started
          </p>
          {isAdminMode && (
            <Badge variant="destructive" className="mt-2">
              Admin Registration
            </Badge>
          )}
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  {isAdminMode ? "Admin Registration" : "Create Account"}
                  {isAdminMode && <Badge variant="outline">Admin</Badge>}
                </CardTitle>
                <CardDescription>
                  {isAdminMode 
                    ? "Create a new admin account with proper authorization" 
                    : "Sign up for a new user account"
                  }
                </CardDescription>
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => {
                  setIsAdminMode(!isAdminMode);
                  setName("");
                  setEmail("");
                  setPassword("");
                  setConfirmPassword("");
                  setLicenseKey("");
                  setAdminSecretKey("");
                }}
                type="button"
              >
                {isAdminMode ? "User Registration" : "Admin Registration"}
              </Button>
            </div>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              {/* Demo Credentials */}
              <div className="p-4 bg-muted/50 rounded-lg border">
                <h4 className="font-medium text-sm mb-2">Demo Credentials for Testing:</h4>
                {isAdminMode ? (
                  <div className="space-y-1 text-xs">
                    <p><strong>Admin Name:</strong> Admin User</p>
                    <p><strong>Admin Email:</strong> admin@example.com</p>
                    <p><strong>Admin Password:</strong> admin123456</p>
                    <p><strong>Admin Secret Key:</strong> ADMIN_SECRET_2024</p>
                  </div>
                ) : (
                  <div className="space-y-1 text-xs">
                    <p><strong>User Name:</strong> Demo User</p>
                    <p><strong>User Email:</strong> user@example.com</p>
                    <p><strong>User Password:</strong> user123456</p>
                    <p><strong>License Key:</strong> LICENSE-ABC123-XYZ789</p>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="name">Full Name</Label>
                <Input
                  id="name"
                  type="text"
                  placeholder="Enter your full name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
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
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <p className="text-xs text-muted-foreground">
                  Must be at least 8 characters long
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
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
                    Contact the platform owner for admin access credentials
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  <Label htmlFor="licenseKey">License Key (Optional)</Label>
                  <Input
                    id="licenseKey"
                    type="text"
                    placeholder="Enter license key if you have one"
                    value={licenseKey}
                    onChange={(e) => setLicenseKey(e.target.value)}
                  />
                  <p className="text-xs text-muted-foreground">
                    You can add your license key later in your account settings
                  </p>
                </div>
              )}

              <Button 
                type="submit" 
                className="w-full" 
                disabled={isLoading}
              >
                {isLoading ? "Creating account..." : (isAdminMode ? "Create Admin Account" : "Create Account")}
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
                disabled={isLoading}
              >
                <Chrome className="mr-2 h-4 w-4" />
                Google
              </Button>
              <Button
                variant="outline"
                className="flex-1"
                disabled={isLoading}
              >
                <Github className="mr-2 h-4 w-4" />
                GitHub
              </Button>
            </div>

            <div className="text-center text-sm">
              <span className="text-muted-foreground">
                Already have an account?{" "}
              </span>
              <Link
                to="/login"
                className="text-primary hover:underline font-medium"
              >
                {isAdminMode ? "Admin Sign in" : "Sign in"}
              </Link>
            </div>
          </CardFooter>
        </Card>

        <div className="text-center text-sm text-muted-foreground space-y-1">
          {isAdminMode ? (
            <>
              <p>Admin registration requires proper authorization</p>
              <p>Contact the platform owner for admin access</p>
            </>
          ) : (
            <>
              <p>By creating an account, you agree to our Terms of Service</p>
              <p>and Privacy Policy</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}