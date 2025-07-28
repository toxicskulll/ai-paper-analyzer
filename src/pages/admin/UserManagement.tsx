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
  Eye,
  Edit,
  UserCheck,
  UserX,
  Trash,
  Plus,
  Filter
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

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

export default function UserManagement() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>("all");

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

  // Export function
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

  // Filter users based on search and status
  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || user.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const stats = [
    { name: "Total Users", value: users.length },
    { name: "Active Users", value: users.filter(u => u.status === "active").length },
    { name: "Suspended Users", value: users.filter(u => u.status === "suspended").length },
    { name: "Admin Users", value: users.filter(u => u.role === "admin").length },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">User Management</h1>
          <p className="text-muted-foreground">
            Manage platform users and their access permissions
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add New User
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.name}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.name}
              </CardTitle>
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
              <CardTitle>User Accounts</CardTitle>
              <CardDescription>View and manage all user accounts</CardDescription>
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
            {/* Search and Filters */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Search className="h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search users..."
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
                  <option value="suspended">Suspended</option>
                </select>
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
    </div>
  );
}
