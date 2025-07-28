import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/context/auth-context";
import { toast } from "sonner";
import { 
  ChevronUp, 
  ChevronDown, 
  Search, 
  Plus, 
  X, 
  Edit, 
  Trash, 
  Users, 
  Key, 
  Activity, 
  Settings, 
  BarChart3,
  Download,
  Filter,
  MoreHorizontal,
  Eye,
  UserCheck,
  UserX,
  AlertTriangle,
  CheckCircle,
  Clock,
  Calendar,
  Mail,
  Shield,
  Database,
  Server
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

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

interface LicenseKey {
  key: string;
  assigned: boolean;
  user?: string;
  created: string;
  expires: string;
  status: "active" | "expired" | "revoked";
  usageCount: number;
}

interface AuditLog {
  id: string;
  userId: string;
  userName: string;
  action: string;
  details: string;
  timestamp: string;
  ipAddress: string;
}

export default function AdminDashboard() {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState("");
  const [newLicenseKey, setNewLicenseKey] = useState("");
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState("overview");

  // Mock data for users
  const [users, setUsers] = useState<User[]>([
    { 
      id: "user-1", 
      name: "Demo User", 
      email: "demo@example.com", 
      role: "user", 
      licenseKey: "LICENSE-123", 
      status: "active",
      authMethod: "email",
      createdAt: "2024-01-01T00:00:00Z",
      lastLogin: "2024-01-15T10:30:00Z"
    },
    { 
      id: "user-2", 
      name: "John Smith", 
      email: "john@example.com", 
      role: "user", 
      licenseKey: "LICENSE-456", 
      status: "active",
      authMethod: "google",
      createdAt: "2024-01-05T00:00:00Z",
      lastLogin: "2024-01-14T15:45:00Z"
    },
    { 
      id: "user-3", 
      name: "Sarah Johnson", 
      email: "sarah@example.com", 
      role: "user", 
      licenseKey: "LICENSE-789", 
      status: "suspended",
      authMethod: "github",
      createdAt: "2024-01-10T00:00:00Z",
      lastLogin: "2024-01-12T09:20:00Z"
    },
    { 
      id: "admin-1", 
      name: "System Administrator", 
      email: "admin@example.com", 
      role: "admin", 
      status: "active",
      authMethod: "email",
      createdAt: "2024-01-01T00:00:00Z",
      lastLogin: "2024-01-15T11:00:00Z"
    },
  ]);

  // Mock data for license keys
  const [licenseKeys, setLicenseKeys] = useState<LicenseKey[]>([
    { key: "LICENSE-123", assigned: true, user: "demo@example.com", created: "2024-01-01", expires: "2025-01-01", status: "active", usageCount: 45 },
    { key: "LICENSE-456", assigned: true, user: "john@example.com", created: "2024-01-05", expires: "2025-01-05", status: "active", usageCount: 32 },
    { key: "LICENSE-789", assigned: true, user: "sarah@example.com", created: "2024-01-10", expires: "2025-01-10", status: "revoked", usageCount: 18 },
    { key: "LICENSE-101", assigned: false, created: "2024-01-15", expires: "2025-01-15", status: "active", usageCount: 0 },
    { key: "LICENSE-202", assigned: false, created: "2024-01-20", expires: "2025-01-20", status: "active", usageCount: 0 },
  ]);

  // Mock audit logs
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([
    { id: "1", userId: "user-1", userName: "Demo User", action: "Login", details: "Successful login via email", timestamp: "2024-01-15T10:30:00Z", ipAddress: "192.168.1.100" },
    { id: "2", userId: "user-2", userName: "John Smith", action: "Paper Upload", details: "Uploaded paper: Neural Networks in Healthcare", timestamp: "2024-01-15T09:15:00Z", ipAddress: "192.168.1.101" },
    { id: "3", userId: "admin-1", userName: "System Administrator", action: "User Suspension", details: "Suspended user: sarah@example.com", timestamp: "2024-01-14T16:20:00Z", ipAddress: "192.168.1.1" },
    { id: "4", userId: "user-3", userName: "Sarah Johnson", action: "License Revoked", details: "License key LICENSE-789 revoked", timestamp: "2024-01-14T16:20:00Z", ipAddress: "192.168.1.1" },
  ]);

  // Analytics data
  const analyticsData = {
    userGrowth: [
      { month: "Jan", users: 12, logins: 45, papers: 23 },
      { month: "Feb", users: 18, logins: 67, papers: 34 },
      { month: "Mar", users: 25, logins: 89, papers: 56 },
      { month: "Apr", users: 32, logins: 112, papers: 78 },
      { month: "May", users: 38, logins: 134, papers: 92 },
      { month: "Jun", users: 45, logins: 156, papers: 108 },
    ],
    licenseUsage: [
      { status: "Active", count: licenseKeys.filter(l => l.status === "active").length },
      { status: "Expired", count: licenseKeys.filter(l => l.status === "expired").length },
      { status: "Revoked", count: licenseKeys.filter(l => l.status === "revoked").length },
    ],
    authMethods: [
      { method: "Email", count: users.filter(u => u.authMethod === "email").length },
      { method: "Google", count: users.filter(u => u.authMethod === "google").length },
      { method: "GitHub", count: users.filter(u => u.authMethod === "github").length },
    ]
  };

  // Platform statistics
  const stats = [
    { 
      name: "Total Users", 
      value: users.length, 
      change: "+5%", 
      changeType: "positive",
      icon: <Users className="h-4 w-4" />
    },
    { 
      name: "Active Licenses", 
      value: licenseKeys.filter(l => l.status === "active").length, 
      change: "+12%", 
      changeType: "positive",
      icon: <Key className="h-4 w-4" />
    },
    { 
      name: "Suspended Users", 
      value: users.filter(u => u.status === "suspended").length, 
      change: "-2", 
      changeType: "negative",
      icon: <UserX className="h-4 w-4" />
    },
    { 
      name: "Daily Logins", 
      value: "156", 
      change: "+8%", 
      changeType: "positive",
      icon: <Activity className="h-4 w-4" />
    },
  ];

  // User management functions
  const suspendUser = (userId: string) => {
    setUsers(users.map(user => 
      user.id === userId ? { ...user, status: "suspended" } : user
    ));
    toast.success("User suspended successfully");
  };

  const activateUser = (userId: string) => {
    setUsers(users.map(user => 
      user.id === userId ? { ...user, status: "active" } : user
    ));
    toast.success("User activated successfully");
  };

  const deleteUser = (userId: string) => {
    setUsers(users.filter(user => user.id !== userId));
    toast.success("User deleted successfully");
  };

  // License management functions
  const generateLicense = () => {
    if (newLicenseKey.trim() === "") {
      toast.error("Please enter a license key");
      return;
    }

    const exists = licenseKeys.some(license => license.key === newLicenseKey);
    if (exists) {
      toast.error("This license key already exists");
      return;
    }

    const newLicense: LicenseKey = {
      key: newLicenseKey,
      assigned: false,
      created: new Date().toISOString().split('T')[0],
      expires: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      status: "active",
      usageCount: 0
    };

    setLicenseKeys([...licenseKeys, newLicense]);
    setNewLicenseKey("");
    toast.success("License key created successfully");
  };

  const revokeLicense = (licenseKey: string) => {
    setLicenseKeys(licenseKeys.map(license => 
      license.key === licenseKey ? { ...license, status: "revoked" } : license
    ));
    toast.success("License key revoked successfully");
  };

  const assignLicense = (licenseKey: string, userEmail: string) => {
    setLicenseKeys(licenseKeys.map(license => 
      license.key === licenseKey ? { ...license, assigned: true, user: userEmail } : license
    ));
    toast.success("License key assigned successfully");
  };

  // Bulk actions
  const handleBulkAction = (action: string) => {
    if (selectedUsers.length === 0) {
      toast.error("Please select users first");
      return;
    }

    switch (action) {
      case "suspend":
        setUsers(users.map(user => 
          selectedUsers.includes(user.id) ? { ...user, status: "suspended" } : user
        ));
        toast.success(`${selectedUsers.length} users suspended`);
        break;
      case "activate":
        setUsers(users.map(user => 
          selectedUsers.includes(user.id) ? { ...user, status: "active" } : user
        ));
        toast.success(`${selectedUsers.length} users activated`);
        break;
      case "delete":
        setUsers(users.filter(user => !selectedUsers.includes(user.id)));
        toast.success(`${selectedUsers.length} users deleted`);
        break;
    }
    setSelectedUsers([]);
  };

  // Export functions
  const exportUsers = () => {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Name,Email,Role,Status,Auth Method,Created,Last Login\n"
      + users.map(user => 
          `${user.name},${user.email},${user.role},${user.status},${user.authMethod},${user.createdAt},${user.lastLogin}`
        ).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "users.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success("Users exported successfully");
  };

  const exportLicenses = () => {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Key,Assigned,User,Status,Created,Expires,Usage Count\n"
      + licenseKeys.map(license => 
          `${license.key},${license.assigned},${license.user || ""},${license.status},${license.created},${license.expires},${license.usageCount}`
        ).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "licenses.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success("Licenses exported successfully");
  };

  const exportAuditLogs = () => {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "User,Action,Details,Timestamp,IP Address\n"
      + auditLogs.map(log => 
          `${log.userName},${log.action},${log.details},${log.timestamp},${log.ipAddress}`
        ).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "audit_logs.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success("Audit logs exported successfully");
  };

  const filteredUsers = users.filter(user => 
    user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Admin Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {user?.name}. Manage your platform and users.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="flex items-center gap-1">
            <Shield className="h-3 w-3" />
            Admin Access
          </Badge>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.name}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.name}
              </CardTitle>
              {stat.icon}
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className={`text-xs ${stat.changeType === "positive" ? "text-green-600" : "text-red-600"}`}>
                {stat.change} from last month
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="users" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            Users
          </TabsTrigger>
          <TabsTrigger value="licenses" className="flex items-center gap-2">
            <Key className="h-4 w-4" />
            Licenses
          </TabsTrigger>
          <TabsTrigger value="audit" className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Audit Logs
          </TabsTrigger>
          <TabsTrigger value="settings" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Settings
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* User Growth Chart */}
            <Card>
              <CardHeader>
                <CardTitle>User Growth & Activity</CardTitle>
                <CardDescription>Monthly user growth and platform activity</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={analyticsData.userGrowth}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="users" stroke="#8884d8" name="Users" />
                    <Line type="monotone" dataKey="logins" stroke="#82ca9d" name="Logins" />
                    <Line type="monotone" dataKey="papers" stroke="#ffc658" name="Papers" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* License Usage Chart */}
            <Card>
              <CardHeader>
                <CardTitle>License Status Distribution</CardTitle>
                <CardDescription>Current license key status breakdown</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={analyticsData.licenseUsage}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ status, percent }) => `${status} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {analyticsData.licenseUsage.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Auth Methods Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Authentication Methods</CardTitle>
                <CardDescription>User authentication method distribution</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analyticsData.authMethods}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="method" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Latest platform activities</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {auditLogs.slice(0, 5).map((log) => (
                    <div key={log.id} className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">{log.userName}</p>
                        <p className="text-xs text-muted-foreground">{log.action}</p>
                        <p className="text-xs text-muted-foreground">{new Date(log.timestamp).toLocaleString()}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Users Tab */}
        <TabsContent value="users" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>User Management</CardTitle>
                  <CardDescription>Manage platform users and their access</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" onClick={exportUsers}>
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Search and Bulk Actions */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Search className="h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search users..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-64"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    {selectedUsers.length > 0 && (
                      <>
                        <Button variant="outline" size="sm" onClick={() => handleBulkAction("suspend")}>
                          <UserX className="h-4 w-4 mr-2" />
                          Suspend ({selectedUsers.length})
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => handleBulkAction("activate")}>
                          <UserCheck className="h-4 w-4 mr-2" />
                          Activate ({selectedUsers.length})
                        </Button>
                        <Button variant="destructive" size="sm" onClick={() => handleBulkAction("delete")}>
                          <Trash className="h-4 w-4 mr-2" />
                          Delete ({selectedUsers.length})
                        </Button>
                      </>
                    )}
                  </div>
                </div>

                {/* Users Table */}
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12">
                        <input
                          type="checkbox"
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedUsers(filteredUsers.map(u => u.id));
                            } else {
                              setSelectedUsers([]);
                            }
                          }}
                        />
                      </TableHead>
                      <TableHead>User</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Auth Method</TableHead>
                      <TableHead>License Key</TableHead>
                      <TableHead>Created</TableHead>
                      <TableHead>Last Login</TableHead>
                      <TableHead className="w-12">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredUsers.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell>
                          <input
                            type="checkbox"
                            checked={selectedUsers.includes(user.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedUsers([...selectedUsers, user.id]);
                              } else {
                                setSelectedUsers(selectedUsers.filter(id => id !== user.id));
                              }
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <div>
                            <div className="font-medium">{user.name}</div>
                            <div className="text-sm text-muted-foreground">{user.email}</div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={user.role === "admin" ? "default" : "secondary"}>
                            {user.role}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant={user.status === "active" ? "default" : "destructive"}>
                            {user.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">
                            {user.authMethod}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {user.licenseKey ? (
                            <code className="text-xs bg-muted px-2 py-1 rounded">
                              {user.licenseKey}
                            </code>
                          ) : (
                            <span className="text-muted-foreground">-</span>
                          )}
                        </TableCell>
                        <TableCell>
                          {new Date(user.createdAt).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          {new Date(user.lastLogin).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="sm">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuLabel>Actions</DropdownMenuLabel>
                              <DropdownMenuItem>
                                <Eye className="h-4 w-4 mr-2" />
                                View Details
                              </DropdownMenuItem>
                              <DropdownMenuItem>
                                <Edit className="h-4 w-4 mr-2" />
                                Edit User
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              {user.status === "active" ? (
                                <DropdownMenuItem onClick={() => suspendUser(user.id)}>
                                  <UserX className="h-4 w-4 mr-2" />
                                  Suspend User
                                </DropdownMenuItem>
                              ) : (
                                <DropdownMenuItem onClick={() => activateUser(user.id)}>
                                  <UserCheck className="h-4 w-4 mr-2" />
                                  Activate User
                                </DropdownMenuItem>
                              )}
                              <DropdownMenuItem 
                                className="text-red-600"
                                onClick={() => deleteUser(user.id)}
                              >
                                <Trash className="h-4 w-4 mr-2" />
                                Delete User
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Licenses Tab */}
        <TabsContent value="licenses" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>License Management</CardTitle>
                  <CardDescription>Manage license keys and their assignments</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" onClick={exportLicenses}>
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Generate New License */}
                <div className="flex items-center gap-2">
                  <Input
                    placeholder="Enter new license key..."
                    value={newLicenseKey}
                    onChange={(e) => setNewLicenseKey(e.target.value)}
                    className="max-w-md"
                  />
                  <Button onClick={generateLicense}>
                    <Plus className="h-4 w-4 mr-2" />
                    Generate
                  </Button>
                </div>

                {/* Licenses Table */}
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>License Key</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Assigned To</TableHead>
                      <TableHead>Created</TableHead>
                      <TableHead>Expires</TableHead>
                      <TableHead>Usage Count</TableHead>
                      <TableHead className="w-12">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {licenseKeys.map((license) => (
                      <TableRow key={license.key}>
                        <TableCell>
                          <code className="text-sm bg-muted px-2 py-1 rounded">
                            {license.key}
                          </code>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant={
                              license.status === "active" ? "default" : 
                              license.status === "expired" ? "secondary" : "destructive"
                            }
                          >
                            {license.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {license.assigned ? (
                            <span className="text-sm">{license.user}</span>
                          ) : (
                            <span className="text-muted-foreground">Unassigned</span>
                          )}
                        </TableCell>
                        <TableCell>{license.created}</TableCell>
                        <TableCell>{license.expires}</TableCell>
                        <TableCell>{license.usageCount}</TableCell>
                        <TableCell>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="sm">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuLabel>Actions</DropdownMenuLabel>
                              {!license.assigned && (
                                <DropdownMenuItem>
                                  <UserCheck className="h-4 w-4 mr-2" />
                                  Assign to User
                                </DropdownMenuItem>
                              )}
                              <DropdownMenuItem>
                                <Edit className="h-4 w-4 mr-2" />
                                Edit License
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              {license.status === "active" && (
                                <DropdownMenuItem 
                                  className="text-red-600"
                                  onClick={() => revokeLicense(license.key)}
                                >
                                  <X className="h-4 w-4 mr-2" />
                                  Revoke License
                                </DropdownMenuItem>
                              )}
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Audit Logs Tab */}
        <TabsContent value="audit" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Audit & Activity Logs</CardTitle>
                  <CardDescription>Track all user and system activities</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" onClick={exportAuditLogs}>
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>User</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Details</TableHead>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>IP Address</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {auditLogs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell>
                        <div className="font-medium">{log.userName}</div>
                        <div className="text-sm text-muted-foreground">{log.userId}</div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{log.action}</Badge>
                      </TableCell>
                      <TableCell className="max-w-md">
                        <p className="text-sm truncate">{log.details}</p>
                      </TableCell>
                      <TableCell>
                        {new Date(log.timestamp).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <code className="text-xs bg-muted px-2 py-1 rounded">
                          {log.ipAddress}
                        </code>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* System Settings */}
            <Card>
              <CardHeader>
                <CardTitle>System Settings</CardTitle>
                <CardDescription>Configure platform-wide settings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Admin Secret Key</Label>
                  <div className="flex items-center gap-2">
                    <Input 
                      type="password" 
                      value="••••••••••••••••" 
                      readOnly 
                      className="font-mono"
                    />
                    <Button variant="outline" size="sm">
                      <Edit className="h-4 w-4" />
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Rotate the global admin secret key
                  </p>
                </div>

                <div className="space-y-2">
                  <Label>User Registration</Label>
                  <Select defaultValue="enabled">
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
                  <Label>OAuth Domains</Label>
                  <Textarea 
                    placeholder="Enter allowed OAuth domains (one per line)"
                    defaultValue="example.com&#10;company.com"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Password Policy</Label>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <input type="checkbox" id="min-length" defaultChecked />
                      <Label htmlFor="min-length">Minimum 8 characters</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input type="checkbox" id="uppercase" defaultChecked />
                      <Label htmlFor="uppercase">Require uppercase</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input type="checkbox" id="numbers" defaultChecked />
                      <Label htmlFor="numbers">Require numbers</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input type="checkbox" id="special" />
                      <Label htmlFor="special">Require special characters</Label>
                    </div>
                  </div>
                </div>

                <Button className="w-full">
                  <Settings className="h-4 w-4 mr-2" />
                  Save Settings
                </Button>
              </CardContent>
            </Card>

            {/* Platform Info */}
            <Card>
              <CardHeader>
                <CardTitle>Platform Information</CardTitle>
                <CardDescription>System status and version details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Platform Version</span>
                    <Badge variant="outline">v2.1.0</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Database Status</span>
                    <Badge variant="default" className="bg-green-500">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Connected
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">API Status</span>
                    <Badge variant="default" className="bg-green-500">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Operational
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Last Backup</span>
                    <span className="text-sm text-muted-foreground">2 hours ago</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">System Uptime</span>
                    <span className="text-sm text-muted-foreground">99.9%</span>
                  </div>
                </div>

                <Separator />

                <div className="space-y-2">
                  <h4 className="text-sm font-medium">Quick Actions</h4>
                  <div className="grid gap-2">
                    <Button variant="outline" size="sm">
                      <Database className="h-4 w-4 mr-2" />
                      Backup Database
                    </Button>
                    <Button variant="outline" size="sm">
                      <Server className="h-4 w-4 mr-2" />
                      System Health Check
                    </Button>
                    <Button variant="outline" size="sm">
                      <Activity className="h-4 w-4 mr-2" />
                      View System Logs
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}