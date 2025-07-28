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
  MoreHorizontal,
  Plus,
  X,
  Edit,
  Key,
  UserCheck,
  Clock,
  AlertTriangle
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface LicenseKey {
  key: string;
  assigned: boolean;
  user?: string;
  created: string;
  expires: string;
  status: "active" | "expired" | "revoked";
  usageCount: number;
}

export default function LicenseManagement() {
  const [searchQuery, setSearchQuery] = useState("");
  const [newLicenseKey, setNewLicenseKey] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  // Mock data for license keys
  const [licenseKeys, setLicenseKeys] = useState<LicenseKey[]>([
    { key: "LICENSE-123", assigned: true, user: "demo@example.com", created: "2024-01-01", expires: "2025-01-01", status: "active", usageCount: 45 },
    { key: "LICENSE-456", assigned: true, user: "john@example.com", created: "2024-01-05", expires: "2025-01-05", status: "active", usageCount: 32 },
    { key: "LICENSE-789", assigned: true, user: "sarah@example.com", created: "2024-01-10", expires: "2025-01-10", status: "revoked", usageCount: 18 },
    { key: "LICENSE-101", assigned: false, created: "2024-01-15", expires: "2025-01-15", status: "active", usageCount: 0 },
    { key: "LICENSE-202", assigned: false, created: "2024-01-20", expires: "2025-01-20", status: "active", usageCount: 0 },
  ]);

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

  // Export function
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

  // Filter licenses based on search and status
  const filteredLicenses = licenseKeys.filter(license => {
    const matchesSearch = license.key.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (license.user && license.user.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesStatus = statusFilter === "all" || license.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const stats = [
    { name: "Total Licenses", value: licenseKeys.length },
    { name: "Active Licenses", value: licenseKeys.filter(l => l.status === "active").length },
    { name: "Assigned Licenses", value: licenseKeys.filter(l => l.assigned).length },
    { name: "Available Licenses", value: licenseKeys.filter(l => !l.assigned && l.status === "active").length },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">License Management</h1>
          <p className="text-muted-foreground">
            Generate and manage license keys for platform access
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
              <Key className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Generate New License */}
      <Card>
        <CardHeader>
          <CardTitle>Generate New License</CardTitle>
          <CardDescription>Create a new license key for platform access</CardDescription>
        </CardHeader>
        <CardContent>
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
        </CardContent>
      </Card>

      {/* Main Content */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>License Keys</CardTitle>
              <CardDescription>View and manage all license keys</CardDescription>
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
            {/* Search and Filters */}
            <div className="flex items-center space-x-2">
              <Search className="h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search licenses..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-64"
              />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-input rounded-md text-sm"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="expired">Expired</option>
                <option value="revoked">Revoked</option>
              </select>
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
                {filteredLicenses.map((license) => (
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
                        <div className="flex items-center gap-2">
                          <UserCheck className="h-4 w-4 text-green-500" />
                          <span className="text-sm">{license.user}</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4 text-muted-foreground" />
                          <span className="text-muted-foreground">Unassigned</span>
                        </div>
                      )}
                    </TableCell>
                    <TableCell>{license.created}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {license.expires}
                        {new Date(license.expires) < new Date() && (
                          <AlertTriangle className="h-4 w-4 text-red-500" />
                        )}
                      </div>
                    </TableCell>
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
    </div>
  );
} 