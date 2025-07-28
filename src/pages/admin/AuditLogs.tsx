import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { 
  Search, 
  Download,
  Filter,
  Activity,
  Clock,
  User,
  Shield,
  AlertTriangle
} from "lucide-react";

interface AuditLog {
  id: string;
  userId: string;
  userName: string;
  action: string;
  details: string;
  timestamp: string;
  ipAddress: string;
  severity: "low" | "medium" | "high";
}

export default function AuditLogs() {
  const [searchQuery, setSearchQuery] = useState("");
  const [actionFilter, setActionFilter] = useState<string>("all");
  const [severityFilter, setSeverityFilter] = useState<string>("all");

  // Mock audit logs
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([
    { 
      id: "1", 
      userId: "user-1", 
      userName: "Demo User", 
      action: "Login", 
      details: "Successful login via email", 
      timestamp: "2024-01-15T10:30:00Z", 
      ipAddress: "192.168.1.100",
      severity: "low"
    },
    { 
      id: "2", 
      userId: "user-2", 
      userName: "John Smith", 
      action: "Paper Upload", 
      details: "Uploaded paper: Neural Networks in Healthcare", 
      timestamp: "2024-01-15T09:15:00Z", 
      ipAddress: "192.168.1.101",
      severity: "low"
    },
    { 
      id: "3", 
      userId: "admin-1", 
      userName: "System Administrator", 
      action: "User Suspension", 
      details: "Suspended user: sarah@example.com", 
      timestamp: "2024-01-14T16:20:00Z", 
      ipAddress: "192.168.1.1",
      severity: "high"
    },
    { 
      id: "4", 
      userId: "user-3", 
      userName: "Sarah Johnson", 
      action: "License Revoked", 
      details: "License key LICENSE-789 revoked", 
      timestamp: "2024-01-14T16:20:00Z", 
      ipAddress: "192.168.1.1",
      severity: "high"
    },
    { 
      id: "5", 
      userId: "user-1", 
      userName: "Demo User", 
      action: "Failed Login", 
      details: "Invalid password attempt", 
      timestamp: "2024-01-15T08:45:00Z", 
      ipAddress: "192.168.1.100",
      severity: "medium"
    },
    { 
      id: "6", 
      userId: "admin-1", 
      userName: "System Administrator", 
      action: "System Settings", 
      details: "Updated admin secret key", 
      timestamp: "2024-01-14T14:30:00Z", 
      ipAddress: "192.168.1.1",
      severity: "high"
    },
  ]);

  // Export function
  const exportAuditLogs = () => {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "User,Action,Details,Timestamp,IP Address,Severity\n"
      + auditLogs.map(log => 
          `${log.userName},${log.action},${log.details},${log.timestamp},${log.ipAddress},${log.severity}`
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

  // Filter logs based on search and filters
  const filteredLogs = auditLogs.filter(log => {
    const matchesSearch = log.userName.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         log.action.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         log.details.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesAction = actionFilter === "all" || log.action === actionFilter;
    const matchesSeverity = severityFilter === "all" || log.severity === severityFilter;
    return matchesSearch && matchesAction && matchesSeverity;
  });

  const stats = [
    { name: "Total Logs", value: auditLogs.length },
    { name: "High Severity", value: auditLogs.filter(l => l.severity === "high").length },
    { name: "Today's Logs", value: auditLogs.filter(l => {
      const today = new Date().toDateString();
      return new Date(l.timestamp).toDateString() === today;
    }).length },
    { name: "Admin Actions", value: auditLogs.filter(l => l.userName.includes("Admin")).length },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high": return "destructive";
      case "medium": return "secondary";
      case "low": return "default";
      default: return "outline";
    }
  };

  const getActionIcon = (action: string) => {
    switch (action.toLowerCase()) {
      case "login": return <User className="h-4 w-4" />;
      case "logout": return <User className="h-4 w-4" />;
      case "user suspension": return <Shield className="h-4 w-4" />;
      case "license revoked": return <AlertTriangle className="h-4 w-4" />;
      case "system settings": return <Shield className="h-4 w-4" />;
      default: return <Activity className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Audit & Activity Logs</h1>
          <p className="text-muted-foreground">
            Track all user and system activities for security and compliance
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.name}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.name}
              </CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Content */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>System Activity Logs</CardTitle>
              <CardDescription>Chronological log of all platform activities</CardDescription>
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
          <div className="space-y-4">
            {/* Search and Filters */}
            <div className="flex items-center space-x-2">
              <Search className="h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search logs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-64"
              />
              <select
                value={actionFilter}
                onChange={(e) => setActionFilter(e.target.value)}
                className="px-3 py-2 border border-input rounded-md text-sm"
              >
                <option value="all">All Actions</option>
                <option value="Login">Login</option>
                <option value="Logout">Logout</option>
                <option value="User Suspension">User Suspension</option>
                <option value="License Revoked">License Revoked</option>
                <option value="System Settings">System Settings</option>
                <option value="Paper Upload">Paper Upload</option>
              </select>
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="px-3 py-2 border border-input rounded-md text-sm"
              >
                <option value="all">All Severity</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            {/* Audit Logs Table */}
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Details</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>IP Address</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredLogs.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{log.userName}</div>
                        <div className="text-sm text-muted-foreground">{log.userId}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getActionIcon(log.action)}
                        <Badge variant="outline">{log.action}</Badge>
                      </div>
                    </TableCell>
                    <TableCell className="max-w-md">
                      <p className="text-sm truncate">{log.details}</p>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getSeverityColor(log.severity)}>
                        {log.severity}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                        {new Date(log.timestamp).toLocaleString()}
                      </div>
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
          </div>
        </CardContent>
      </Card>
    </div>
  );
}