import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Activity as ActivityIcon,
  Calendar as CalendarIcon,
  Clock,
  FileText,
  Filter,
  Search,
  BookOpen,
  Download,
  Upload,
  Trash2,
  Star,
  PenLine,
  Check,
  AlertCircle,
} from "lucide-react";
import { format } from "date-fns";

// Mock data for activity log
const initialActivityData = [
  {
    id: "act1",
    type: "analysis",
    title: "Paper analysis completed",
    description:
      "Analysis completed for 'Transformer-based Models for Natural Language Processing'",
    timestamp: "2023-11-15T14:30:00",
    status: "success",
  },
  {
    id: "act2",
    type: "library",
    title: "Paper added to library",
    description: "Added 'Quantum Computing Applications in Finance' to library",
    timestamp: "2023-11-15T10:15:00",
    status: "success",
  },
  {
    id: "act3",
    type: "download",
    title: "Paper downloaded",
    description:
      "Downloaded 'Climate Change Effects on Marine Biodiversity: A Meta-analysis'",
    timestamp: "2023-11-14T16:45:00",
    status: "success",
  },
  {
    id: "act4",
    type: "search",
    title: "Search performed",
    description: "Searched for 'AI ethics healthcare'",
    timestamp: "2023-11-14T09:20:00",
    status: "success",
  },
  {
    id: "act5",
    type: "analysis",
    title: "Analysis failed",
    description:
      "Analysis failed for 'Sustainable Energy Storage Systems for Renewable Integration'",
    timestamp: "2023-11-13T11:05:00",
    status: "error",
  },
  {
    id: "act6",
    type: "favorite",
    title: "Paper marked as favorite",
    description:
      "Marked 'Ethical Considerations in AI-driven Healthcare Decision Support Systems' as favorite",
    timestamp: "2023-11-12T14:50:00",
    status: "success",
  },
  {
    id: "act7",
    type: "upload",
    title: "Paper uploaded",
    description: "Uploaded 'Machine Learning for Image Recognition in Medical Diagnostics'",
    timestamp: "2023-11-12T10:30:00",
    status: "success",
  },
  {
    id: "act8",
    type: "note",
    title: "Note added",
    description: "Added note to 'Advances in Deep Learning: A Comprehensive Survey'",
    timestamp: "2023-11-11T16:15:00",
    status: "success",
  },
  {
    id: "act9",
    type: "delete",
    title: "Paper deleted",
    description: "Deleted 'Outdated Research Methods in Social Sciences'",
    timestamp: "2023-11-10T09:45:00",
    status: "warning",
  },
  {
    id: "act10",
    type: "analysis",
    title: "Paper analysis started",
    description:
      "Started analysis for 'Recent Developments in Renewable Energy Technologies'",
    timestamp: "2023-11-10T08:30:00",
    status: "pending",
  },
];

export default function ActivityLog() {
  const [activities, setActivities] = useState(initialActivityData);
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [dateFilter, setDateFilter] = useState<Date | undefined>(undefined);

  // Filter activities based on search query, type, status, and date
  const filteredActivities = activities.filter((activity) => {
    // Search filter
    const matchesSearch =
      searchQuery === "" ||
      activity.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      activity.description.toLowerCase().includes(searchQuery.toLowerCase());

    // Type filter
    const matchesType = typeFilter === "all" || activity.type === typeFilter;

    // Status filter
    const matchesStatus =
      statusFilter === "all" || activity.status === statusFilter;

    // Date filter
    const matchesDate =
      !dateFilter ||
      new Date(activity.timestamp).toDateString() === dateFilter.toDateString();

    return matchesSearch && matchesType && matchesStatus && matchesDate;
  });

  // Reset all filters
  const resetFilters = () => {
    setSearchQuery("");
    setTypeFilter("all");
    setStatusFilter("all");
    setDateFilter(undefined);
  };

  // Helper function to get activity icon based on type
  const getActivityIcon = (type: string, status: string) => {
    switch (type) {
      case "analysis":
        return <FileText className="h-4 w-4" />;
      case "library":
        return <BookOpen className="h-4 w-4" />;
      case "download":
        return <Download className="h-4 w-4" />;
      case "search":
        return <Search className="h-4 w-4" />;
      case "favorite":
        return <Star className="h-4 w-4" />;
      case "upload":
        return <Upload className="h-4 w-4" />;
      case "note":
        return <PenLine className="h-4 w-4" />;
      case "delete":
        return <Trash2 className="h-4 w-4" />;
      default:
        return <ActivityIcon className="h-4 w-4" />;
    }
  };

  // Helper function to get status badge color
  const getStatusBadge = (status: string) => {
    switch (status) {
      case "success":
        return (
          <Badge variant="outline" className="border-green-500 text-green-500">
            <Check className="mr-1 h-3 w-3" /> Success
          </Badge>
        );
      case "error":
        return (
          <Badge variant="outline" className="border-red-500 text-red-500">
            <AlertCircle className="mr-1 h-3 w-3" /> Error
          </Badge>
        );
      case "warning":
        return (
          <Badge variant="outline" className="border-yellow-500 text-yellow-500">
            <AlertCircle className="mr-1 h-3 w-3" /> Warning
          </Badge>
        );
      case "pending":
        return (
          <Badge variant="outline" className="border-blue-500 text-blue-500">
            <Clock className="mr-1 h-3 w-3" /> Pending
          </Badge>
        );
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return format(date, "PPp"); // Format as "Apr 29, 2023, 1:30 PM"
  };

  // Group activities by date for better organization
  const groupActivitiesByDate = (activities: typeof initialActivityData) => {
    const grouped: Record<string, typeof initialActivityData> = {};

    activities.forEach((activity) => {
      const date = new Date(activity.timestamp).toDateString();
      if (!grouped[date]) {
        grouped[date] = [];
      }
      grouped[date].push(activity);
    });

    return Object.entries(grouped).sort(
      ([dateA], [dateB]) =>
        new Date(dateB).getTime() - new Date(dateA).getTime()
    );
  };

  const groupedActivities = groupActivitiesByDate(filteredActivities);

  return (
    <div className="space-y-6">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Activity Log</h1>
        <p className="text-muted-foreground">
          Track and review your research activities
        </p>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle>Filters</CardTitle>
          <CardDescription>
            Narrow down activities by type, status, or date
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Search activities..."
                className="pl-8"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="analysis">Analysis</SelectItem>
                <SelectItem value="library">Library</SelectItem>
                <SelectItem value="download">Download</SelectItem>
                <SelectItem value="search">Search</SelectItem>
                <SelectItem value="favorite">Favorite</SelectItem>
                <SelectItem value="upload">Upload</SelectItem>
                <SelectItem value="note">Note</SelectItem>
                <SelectItem value="delete">Delete</SelectItem>
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="success">Success</SelectItem>
                <SelectItem value="error">Error</SelectItem>
                <SelectItem value="warning">Warning</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
              </SelectContent>
            </Select>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={`w-[240px] justify-start text-left font-normal ${
                    dateFilter ? "" : "text-muted-foreground"
                  }`}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {dateFilter ? format(dateFilter, "PPP") : "Filter by date"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar
                  mode="single"
                  selected={dateFilter}
                  onSelect={setDateFilter}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
            <Button variant="ghost" onClick={resetFilters}>
              Reset Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Activity List */}
      <div className="space-y-6">
        {filteredActivities.length === 0 ? (
          <div className="flex flex-col items-center justify-center border rounded-lg p-8">
            <ActivityIcon className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium">No activities found</h3>
            <p className="text-sm text-muted-foreground text-center mt-1">
              Try adjusting your filters or search criteria
            </p>
            <Button className="mt-4" onClick={resetFilters}>
              Reset Filters
            </Button>
          </div>
        ) : (
          groupedActivities.map(([date, activities]) => (
            <div key={date} className="space-y-4">
              <div className="sticky top-0 z-10 flex items-center gap-2 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 py-2">
                <CalendarIcon className="h-4 w-4 text-muted-foreground" />
                <h2 className="font-medium">
                  {new Date(date).toLocaleDateString("en-US", {
                    weekday: "long",
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </h2>
              </div>

              <div className="space-y-4">
                {activities.map((activity) => (
                  <Card key={activity.id}>
                    <CardContent className="p-4">
                      <div className="flex items-start gap-4">
                        <div className="rounded-full bg-primary/10 p-2">
                          {getActivityIcon(activity.type, activity.status)}
                        </div>
                        <div className="flex-1 space-y-1">
                          <div className="flex items-center justify-between">
                            <p className="font-medium">{activity.title}</p>
                            {getStatusBadge(activity.status)}
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {activity.description}
                          </p>
                          <div className="flex items-center text-xs text-muted-foreground">
                            <Clock className="mr-1 h-3 w-3" />
                            <span>
                              {formatDate(activity.timestamp)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      {filteredActivities.length > 0 && (
        <Pagination>
          <PaginationContent>
            <PaginationItem>
              <PaginationPrevious href="#" />
            </PaginationItem>
            <PaginationItem>
              <PaginationLink href="#" isActive>
                1
              </PaginationLink>
            </PaginationItem>
            <PaginationItem>
              <PaginationLink href="#">2</PaginationLink>
            </PaginationItem>
            <PaginationItem>
              <PaginationLink href="#">3</PaginationLink>
            </PaginationItem>
            <PaginationItem>
              <PaginationEllipsis />
            </PaginationItem>
            <PaginationItem>
              <PaginationNext href="#" />
            </PaginationItem>
          </PaginationContent>
        </Pagination>
      )}
    </div>
  );
}