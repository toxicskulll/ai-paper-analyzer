import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { 
  Settings,
  Shield,
  Database,
  Server,
  Key,
  Users,
  AlertTriangle,
  CheckCircle,
  Clock,
  Save,
  RotateCcw,
  Eye,
  EyeOff
} from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function SystemSettings() {
  const [showSecretKey, setShowSecretKey] = useState(false);
  const [settings, setSettings] = useState({
    adminSecretKey: "ADMIN-SECRET-2024",
    userRegistration: "enabled",
    oauthDomains: "example.com\ncompany.com\nuniversity.edu",
    passwordPolicy: {
      minLength: 8,
      requireUppercase: true,
      requireNumbers: true,
      requireSpecial: false,
    },
    sessionTimeout: "24h",
    maxLoginAttempts: 5,
    enableAuditLogs: true,
    enableNotifications: true,
  });

  const [systemInfo] = useState({
    version: "v2.1.0",
    databaseStatus: "Connected",
    apiStatus: "Operational",
    lastBackup: "2 hours ago",
    systemUptime: "99.9%",
    storageUsage: "78%",
    memoryUsage: "62%",
    cpuUsage: "45%",
  });

  const handleSaveSettings = () => {
    toast.success("Settings saved successfully");
  };

  const rotateSecretKey = () => {
    const newKey = "ADMIN-SECRET-" + Math.random().toString(36).substring(2, 15);
    setSettings({ ...settings, adminSecretKey: newKey });
    toast.success("Admin secret key rotated successfully");
  };

  const backupDatabase = () => {
    toast.success("Database backup initiated");
  };

  const healthCheck = () => {
    toast.success("System health check completed");
  };

  const viewLogs = () => {
    toast.info("Opening system logs...");
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">System Settings</h1>
          <p className="text-muted-foreground">
            Configure platform-wide settings and security policies
          </p>
        </div>
        <Button onClick={handleSaveSettings}>
          <Save className="h-4 w-4 mr-2" />
          Save Settings
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Security Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Security Settings
            </CardTitle>
            <CardDescription>Configure security policies and access controls</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Admin Secret Key</Label>
              <div className="flex items-center gap-2">
                <Input 
                  type={showSecretKey ? "text" : "password"} 
                  value={settings.adminSecretKey} 
                  readOnly 
                  className="font-mono"
                />
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => setShowSecretKey(!showSecretKey)}
                >
                  {showSecretKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
                <Button variant="outline" size="sm" onClick={rotateSecretKey}>
                  <RotateCcw className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Rotate the global admin secret key for enhanced security
              </p>
            </div>

            <div className="space-y-2">
              <Label>User Registration</Label>
              <Select 
                value={settings.userRegistration} 
                onValueChange={(value) => setSettings({ ...settings, userRegistration: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="enabled">Enabled</SelectItem>
                  <SelectItem value="disabled">Disabled</SelectItem>
                  <SelectItem value="invite-only">Invite Only</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Session Timeout</Label>
              <Select 
                value={settings.sessionTimeout} 
                onValueChange={(value) => setSettings({ ...settings, sessionTimeout: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1h">1 hour</SelectItem>
                  <SelectItem value="8h">8 hours</SelectItem>
                  <SelectItem value="24h">24 hours</SelectItem>
                  <SelectItem value="7d">7 days</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Maximum Login Attempts</Label>
              <Input 
                type="number" 
                value={settings.maxLoginAttempts}
                onChange={(e) => setSettings({ ...settings, maxLoginAttempts: parseInt(e.target.value) })}
                min="1"
                max="10"
              />
            </div>
          </CardContent>
        </Card>

        {/* Authentication Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Key className="h-5 w-5" />
              Authentication Settings
            </CardTitle>
            <CardDescription>Configure OAuth and password policies</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>OAuth Domains</Label>
              <Textarea 
                placeholder="Enter allowed OAuth domains (one per line)"
                value={settings.oauthDomains}
                onChange={(e) => setSettings({ ...settings, oauthDomains: e.target.value })}
                rows={4}
              />
              <p className="text-xs text-muted-foreground">
                Only users from these domains can use OAuth authentication
              </p>
            </div>

            <Separator />

            <div className="space-y-2">
              <Label>Password Policy</Label>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    id="min-length" 
                    checked={settings.passwordPolicy.minLength >= 8}
                    onChange={(e) => setSettings({
                      ...settings,
                      passwordPolicy: {
                        ...settings.passwordPolicy,
                        minLength: e.target.checked ? 8 : 6
                      }
                    })}
                  />
                  <Label htmlFor="min-length">Minimum 8 characters</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    id="uppercase" 
                    checked={settings.passwordPolicy.requireUppercase}
                    onChange={(e) => setSettings({
                      ...settings,
                      passwordPolicy: {
                        ...settings.passwordPolicy,
                        requireUppercase: e.target.checked
                      }
                    })}
                  />
                  <Label htmlFor="uppercase">Require uppercase letters</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    id="numbers" 
                    checked={settings.passwordPolicy.requireNumbers}
                    onChange={(e) => setSettings({
                      ...settings,
                      passwordPolicy: {
                        ...settings.passwordPolicy,
                        requireNumbers: e.target.checked
                      }
                    })}
                  />
                  <Label htmlFor="numbers">Require numbers</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    id="special" 
                    checked={settings.passwordPolicy.requireSpecial}
                    onChange={(e) => setSettings({
                      ...settings,
                      passwordPolicy: {
                        ...settings.passwordPolicy,
                        requireSpecial: e.target.checked
                      }
                    })}
                  />
                  <Label htmlFor="special">Require special characters</Label>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* System Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Server className="h-5 w-5" />
              System Information
            </CardTitle>
            <CardDescription>Platform status and version details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Platform Version</span>
                <Badge variant="outline">{systemInfo.version}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Database Status</span>
                <Badge variant="default" className="bg-green-500">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  {systemInfo.databaseStatus}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">API Status</span>
                <Badge variant="default" className="bg-green-500">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  {systemInfo.apiStatus}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Last Backup</span>
                <span className="text-sm text-muted-foreground">{systemInfo.lastBackup}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">System Uptime</span>
                <span className="text-sm text-muted-foreground">{systemInfo.systemUptime}</span>
              </div>
            </div>

            <Separator />

            <div className="space-y-2">
              <h4 className="text-sm font-medium">Resource Usage</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Storage</span>
                  <div className="flex items-center gap-2">
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${parseInt(systemInfo.storageUsage) > 70 ? 'bg-red-500' : 'bg-green-500'}`}
                        style={{ width: systemInfo.storageUsage }}
                      ></div>
                    </div>
                    <span className="text-sm">{systemInfo.storageUsage}</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Memory</span>
                  <div className="flex items-center gap-2">
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div 
                        className="h-2 rounded-full bg-blue-500"
                        style={{ width: systemInfo.memoryUsage }}
                      ></div>
                    </div>
                    <span className="text-sm">{systemInfo.memoryUsage}</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">CPU</span>
                  <div className="flex items-center gap-2">
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div 
                        className="h-2 rounded-full bg-green-500"
                        style={{ width: systemInfo.cpuUsage }}
                      ></div>
                    </div>
                    <span className="text-sm">{systemInfo.cpuUsage}</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Quick Actions
            </CardTitle>
            <CardDescription>System maintenance and monitoring tools</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <h4 className="text-sm font-medium">System Maintenance</h4>
              <div className="grid gap-2">
                <Button variant="outline" size="sm" onClick={backupDatabase}>
                  <Database className="h-4 w-4 mr-2" />
                  Backup Database
                </Button>
                <Button variant="outline" size="sm" onClick={healthCheck}>
                  <Server className="h-4 w-4 mr-2" />
                  System Health Check
                </Button>
                <Button variant="outline" size="sm" onClick={viewLogs}>
                  <AlertTriangle className="h-4 w-4 mr-2" />
                  View System Logs
                </Button>
              </div>
            </div>

            <Separator />

            <div className="space-y-2">
              <h4 className="text-sm font-medium">Feature Toggles</h4>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    id="audit-logs" 
                    checked={settings.enableAuditLogs}
                    onChange={(e) => setSettings({ ...settings, enableAuditLogs: e.target.checked })}
                  />
                  <Label htmlFor="audit-logs">Enable Audit Logs</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    id="notifications" 
                    checked={settings.enableNotifications}
                    onChange={(e) => setSettings({ ...settings, enableNotifications: e.target.checked })}
                  />
                  <Label htmlFor="notifications">Enable Notifications</Label>
                </div>
              </div>
            </div>

            <Separator />

            <div className="space-y-2">
              <h4 className="text-sm font-medium">System Alerts</h4>
              <div className="space-y-2">
                <div className="p-3 bg-yellow-50 dark:bg-yellow-950 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <AlertTriangle className="h-4 w-4 text-yellow-600" />
                    <span className="text-sm font-medium text-yellow-800 dark:text-yellow-200">Storage Warning</span>
                  </div>
                  <p className="text-xs text-yellow-700 dark:text-yellow-300">
                    Storage usage is at 78%. Consider expanding storage capacity.
                  </p>
                </div>
                <div className="p-3 bg-green-50 dark:bg-green-950 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium text-green-800 dark:text-green-200">System Healthy</span>
                  </div>
                  <p className="text-xs text-green-700 dark:text-green-300">
                    All systems are operating normally.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}