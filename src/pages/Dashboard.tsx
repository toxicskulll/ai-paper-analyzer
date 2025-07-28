import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/context/auth-context";
import { Activity, BookOpen, Clock, FileText, TrendingUp, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Link } from "react-router-dom";

export default function Dashboard() {
  const { user } = useAuth();

  // Mock data for dashboard
  const stats = [
    {
      title: "Papers Analyzed",
      value: "28",
      description: "Last 30 days",
      change: "+4%",
      icon: <FileText className="h-4 w-4" />,
    },
    {
      title: "Papers in Library",
      value: "152",
      description: "Total collection",
      change: "+12",
      icon: <BookOpen className="h-4 w-4" />,
    },
    {
      title: "Analysis Time Saved",
      value: "46h",
      description: "This month",
      change: "+20%",
      icon: <Clock className="h-4 w-4" />,
    },
    {
      title: "Research Network",
      value: "34",
      description: "Connected researchers",
      change: "+3",
      icon: <Users className="h-4 w-4" />,
    },
  ];

  const recentActivity = [
    {
      id: 1,
      action: "Paper analyzed",
      subject: "Neural Networks in Healthcare: A Comprehensive Review",
      timestamp: "2 hours ago",
      icon: <Activity className="h-4 w-4 text-primary" />,
    },
    {
      id: 2,
      action: "Paper added to library",
      subject: "Quantum Computing Applications in Finance",
      timestamp: "5 hours ago",
      icon: <BookOpen className="h-4 w-4 text-green-500" />,
    },
    {
      id: 3,
      action: "Analysis completed",
      subject: "Climate Change Effects on Ocean Ecosystems",
      timestamp: "Yesterday",
      icon: <FileText className="h-4 w-4 text-blue-500" />,
    },
  ];

  const researchTrends = [
    { name: "Machine Learning", percentage: 85 },
    { name: "Quantum Computing", percentage: 65 },
    { name: "Climate Science", percentage: 45 },
    { name: "Biotechnology", percentage: 70 },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome section */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Welcome back, {user?.name}!</h1>
        <p className="text-muted-foreground">
          Here's an overview of your research activities and insights.
        </p>
      </div>

      {/* Quick action buttons */}
      <div className="flex flex-wrap gap-2">
        <Button asChild>
          <Link to="/scraper">Scrape New Papers</Link>
        </Button>
        <Button variant="outline" asChild>
          <Link to="/library">Browse Library</Link>
        </Button>
        <Button variant="secondary" asChild>
          <Link to="/analyzer">Analyze Paper</Link>
        </Button>
      </div>

      {/* Stats grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <div className="h-4 w-4 text-muted-foreground">
                {stat.icon}
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">
                {stat.description}{" "}
                <span className="text-green-500">{stat.change}</span>
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main content grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {/* Recent activity */}
        <Card className="lg:col-span-4">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Your latest research actions and updates
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-start gap-4 rounded-md border p-3"
                >
                  <div className="rounded-full bg-primary/10 p-2">
                    {activity.icon}
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{activity.action}</p>
                    <p className="text-sm text-muted-foreground line-clamp-1">
                      {activity.subject}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {activity.timestamp}
                    </p>
                  </div>
                </div>
              ))}
              <Button variant="ghost" className="w-full">
                View all activity
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Research trends */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Research Trends</CardTitle>
            <CardDescription>
              Popular topics in your field
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {researchTrends.map((trend) => (
                <div key={trend.name} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-primary" />
                      <span className="text-sm font-medium">{trend.name}</span>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {trend.percentage}%
                    </span>
                  </div>
                  <Progress value={trend.percentage} />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recommended papers */}
      <Card>
        <CardHeader>
          <CardTitle>Recommended Papers</CardTitle>
          <CardDescription>
            Based on your research interests and recent activity
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="overflow-hidden">
                <div className="p-4">
                  <h3 className="font-semibold line-clamp-2">
                    Advancements in Natural Language Processing: A {i}0-Year Review
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    By Authors et al. • 202{i+1}
                  </p>
                  <p className="text-sm mt-2 line-clamp-3">
                    This comprehensive review explores the evolution of NLP technologies over the past decade, highlighting key breakthroughs in transformer models, semantic understanding, and multilingual capabilities.
                  </p>
                  <div className="flex items-center gap-2 mt-3">
                    <Button variant="secondary" size="sm">
                      Add to Library
                    </Button>
                    <Button variant="outline" size="sm">
                      Analyze
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}