import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  BarChart3,
  Users,
  Key,
  Activity,
  TrendingUp,
  TrendingDown,
  Calendar,
  Clock,
  Database,
  Server,
  Download
} from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';

export default function Analytics() {
  const [timeRange, setTimeRange] = useState("30d");

  // Mock analytics data
  const analyticsData = {
    userGrowth: [
      { month: "Jan", users: 12, logins: 45, papers: 23 },
      { month: "Feb", users: 18, logins: 67, papers: 34 },
      { month: "Mar", users: 25, logins: 89, papers: 56 },
      { month: "Apr", users: 32, logins: 112, papers: 78 },
      { month: "May", users: 38, logins: 134, papers: 92 },
      { month: "Jun", users: 45, logins: 156, papers: 108 },
    ],
    dailyActivity: [
      { day: "Mon", logins: 45, uploads: 12, analyses: 8 },
      { day: "Tue", logins: 52, uploads: 15, analyses: 11 },
      { day: "Wed", logins: 48, uploads: 13, analyses: 9 },
      { day: "Thu", logins: 61, uploads: 18, analyses: 14 },
      { day: "Fri", logins: 55, uploads: 16, analyses: 12 },
      { day: "Sat", logins: 38, uploads: 10, analyses: 7 },
      { day: "Sun", logins: 42, uploads: 11, analyses: 8 },
    ],
    licenseUsage: [
      { status: "Active", count: 85, percentage: 70 },
      { status: "Expired", count: 15, percentage: 12 },
      { status: "Revoked", count: 8, percentage: 7 },
      { status: "Unassigned", count: 12, percentage: 11 },
    ],
    authMethods: [
      { method: "Email", count: 45, percentage: 60 },
      { method: "Google", count: 20, percentage: 27 },
      { method: "GitHub", count: 10, percentage: 13 },
    ],
    topUsers: [
      { name: "Demo User", papers: 15, analyses: 23, lastActive: "2 hours ago" },
      { name: "John Smith", papers: 12, analyses: 18, lastActive: "5 hours ago" },
      { name: "Sarah Johnson", papers: 8, analyses: 14, lastActive: "1 day ago" },
      { name: "Mike Wilson", papers: 6, analyses: 11, lastActive: "2 days ago" },
    ],
    systemMetrics: [
      { metric: "CPU Usage", value: "45%", status: "normal", trend: "stable" },
      { metric: "Memory Usage", value: "62%", status: "normal", trend: "stable" },
      { metric: "Storage Usage", value: "78%", status: "warning", trend: "increasing" },
      { metric: "Network Load", value: "23%", status: "normal", trend: "stable" },
    ]
  };

  const stats = [
    { 
      name: "Total Users", 
      value: "156", 
      change: "+12%", 
      changeType: "positive",
      icon: <Users className="h-4 w-4" />
    },
    { 
      name: "Active Licenses", 
      value: "142", 
      change: "+8%", 
      changeType: "positive",
      icon: <Key className="h-4 w-4" />
    },
    { 
      name: "Papers Analyzed", 
      value: "1,234", 
      change: "+23%", 
      changeType: "positive",
      icon: <Activity className="h-4 w-4" />
    },
    { 
      name: "System Uptime", 
      value: "99.9%", 
      change: "+0.1%", 
      changeType: "positive",
      icon: <Server className="h-4 w-4" />
    },
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "normal": return "bg-green-500";
      case "warning": return "bg-yellow-500";
      case "critical": return "bg-red-500";
      default: return "bg-gray-500";
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "increasing": return <TrendingUp className="h-4 w-4 text-red-500" />;
      case "decreasing": return <TrendingDown className="h-4 w-4 text-green-500" />;
      case "stable": return <div className="h-4 w-4 text-blue-500">—</div>;
      default: return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics & Insights</h1>
          <p className="text-muted-foreground">
            Comprehensive platform analytics and performance metrics
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-input rounded-md text-sm"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
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
                {stat.change} from last period
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* User Growth Chart */}
        <Card>
          <CardHeader>
            <CardTitle>User Growth & Activity</CardTitle>
            <CardDescription>Monthly user growth and platform activity trends</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analyticsData.userGrowth}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="users" stroke="#8884d8" name="Users" strokeWidth={2} />
                <Line type="monotone" dataKey="logins" stroke="#82ca9d" name="Logins" strokeWidth={2} />
                <Line type="monotone" dataKey="papers" stroke="#ffc658" name="Papers" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Daily Activity Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Daily Activity</CardTitle>
            <CardDescription>Weekly activity patterns and usage trends</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={analyticsData.dailyActivity}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="logins" stackId="1" stroke="#8884d8" fill="#8884d8" />
                <Area type="monotone" dataKey="uploads" stackId="1" stroke="#82ca9d" fill="#82ca9d" />
                <Area type="monotone" dataKey="analyses" stackId="1" stroke="#ffc658" fill="#ffc658" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* License Usage Distribution */}
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
                  label={({ status, percentage }) => `${status} ${percentage}%`}
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

        {/* Authentication Methods */}
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
      </div>

      {/* Additional Analytics */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Top Users */}
        <Card>
          <CardHeader>
            <CardTitle>Top Active Users</CardTitle>
            <CardDescription>Users with highest activity levels</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analyticsData.topUsers.map((user, index) => (
                <div key={user.name} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-white text-sm font-bold">
                      {index + 1}
                    </div>
                    <div>
                      <div className="font-medium">{user.name}</div>
                      <div className="text-sm text-muted-foreground">
                        {user.papers} papers • {user.analyses} analyses
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-muted-foreground">{user.lastActive}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* System Metrics */}
        <Card>
          <CardHeader>
            <CardTitle>System Performance</CardTitle>
            <CardDescription>Real-time system health metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analyticsData.systemMetrics.map((metric) => (
                <div key={metric.metric} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(metric.status)}`}></div>
                    <div>
                      <div className="font-medium">{metric.metric}</div>
                      <div className="text-sm text-muted-foreground">{metric.trend}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="text-lg font-bold">{metric.value}</div>
                    {getTrendIcon(metric.trend)}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Key Insights</CardTitle>
          <CardDescription>Automated insights and recommendations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="p-4 bg-green-50 dark:bg-green-950 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="h-4 w-4 text-green-600" />
                <span className="font-medium text-green-800 dark:text-green-200">Growth Trend</span>
              </div>
              <p className="text-sm text-green-700 dark:text-green-300">
                User growth is up 12% this month, indicating strong platform adoption.
              </p>
            </div>
            <div className="p-4 bg-blue-50 dark:bg-blue-950 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="h-4 w-4 text-blue-600" />
                <span className="font-medium text-blue-800 dark:text-blue-200">Activity Peak</span>
              </div>
              <p className="text-sm text-blue-700 dark:text-blue-300">
                Peak activity occurs on Thursdays with 61 daily logins on average.
              </p>
            </div>
            <div className="p-4 bg-yellow-50 dark:bg-yellow-950 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Database className="h-4 w-4 text-yellow-600" />
                <span className="font-medium text-yellow-800 dark:text-yellow-200">Storage Alert</span>
              </div>
              <p className="text-sm text-yellow-700 dark:text-yellow-300">
                Storage usage at 78%. Consider expanding storage capacity soon.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}