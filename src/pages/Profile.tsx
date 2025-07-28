import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import {
  User,
  Settings,
  Bell,
  Lock,
  FileText,
  Trash2,
  Mail,
  BookOpen,
  Key,
  Check,
  Download,
  RotateCcw,
  Eye,
  EyeOff,
  Plus,
  Copy,
} from "lucide-react";
import { useAuth } from "@/context/auth-context";
import { toast } from "sonner";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";

// IEEE Credentials section component with secret key functionality
const IEEECredentialsSection = () => {
  const [secretKeyInput, setSecretKeyInput] = useState("");
  const [isVisible, setIsVisible] = useState(false);
  const [credentials, setCredentials] = useState({
    username: "researcher_1234",
    password: "••••••••••••",
    accessToken: "ieee_xplore_token_9876543210",
    apiKey: "ieee_api_key_abcdefg12345"
  });
  
  // Check if the entered key matches the secret key
  const checkSecretKey = () => {
    const secretKey = "ieeexplore123"; // In a real app, this would be more secure
    
    if (secretKeyInput === secretKey) {
      setIsVisible(true);
      toast.success("IEEE credentials unlocked");
    } else {
      toast.error("Invalid secret key");
    }
  };
  
  // Hide credentials
  const hideCredentials = () => {
    setIsVisible(false);
    setSecretKeyInput("");
  };

  return (
    <div className="mt-4 border rounded-md p-4">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-md font-semibold">IEEE Xplore Credentials</h3>
          <p className="text-sm text-muted-foreground">
            Enter the secret key to view your IEEE Xplore credentials
          </p>
        </div>
        <Badge variant={isVisible ? "destructive" : "outline"}>
          {isVisible ? "Exposed" : "Protected"}
        </Badge>
      </div>

      {!isVisible ? (
        <div className="flex gap-2">
          <Input
            type="password"
            placeholder="Enter secret key"
            value={secretKeyInput}
            onChange={(e) => setSecretKeyInput(e.target.value)}
          />
          <Button onClick={checkSecretKey}>
            <Eye className="h-4 w-4 mr-2" /> Unlock
          </Button>
        </div>
      ) : (
        <div className="space-y-3 animate-in fade-in slide-in-from-top-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="ieee-username">IEEE Username</Label>
              <Input
                id="ieee-username"
                value={credentials.username}
                readOnly
              />
            </div>
            <div>
              <Label htmlFor="ieee-password">IEEE Password</Label>
              <Input
                id="ieee-password"
                type="password"
                value={credentials.password}
                readOnly
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="ieee-token">Access Token</Label>
              <Input
                id="ieee-token"
                value={credentials.accessToken}
                readOnly
              />
            </div>
            <div>
              <Label htmlFor="ieee-apikey">API Key</Label>
              <Input
                id="ieee-apikey"
                value={credentials.apiKey}
                readOnly
              />
            </div>
          </div>
          <div className="flex justify-end mt-2">
            <Button variant="outline" onClick={hideCredentials}>
              <EyeOff className="h-4 w-4 mr-2" /> Hide Credentials
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default function Profile() {
  const { user, logout } = useAuth();

  // Profile form state
  const [profileForm, setProfileForm] = useState({
    name: user?.name || "",
    email: user?.email || "",
    bio: "Researcher in computational linguistics and AI with a focus on NLP applications in academic search.",
    institution: "Stanford University",
    role: "Research Scientist",
    website: "https://example.com",
  });

  // Notification settings state
  const [notificationSettings, setNotificationSettings] = useState({
    email: true,
    newPapers: true,
    analysisCompleted: true,
    weeklyDigest: false,
    papersRelatedToYourInterests: true,
    appUpdates: false,
  });

  // API key state
  const [apiKeys, setApiKeys] = useState([
    {
      id: "key-1",
      name: "Research App Integration",
      created: "2023-09-15",
      lastUsed: "2023-10-28",
    },
  ]);

  // Preferences state
  const [preferences, setPreferences] = useState({
    theme: "system",
    language: "english",
    paperDisplay: "compact",
    aiSummarization: "detailed",
    citationFormat: "apa",
  });

  // Handle profile form changes
  const handleProfileChange = (field: string, value: string) => {
    setProfileForm((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  // Handle notification toggle
  const handleNotificationToggle = (field: string, value: boolean) => {
    setNotificationSettings((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  // Handle preference change
  const handlePreferenceChange = (field: string, value: string) => {
    setPreferences((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success("Profile updated successfully!");
  };

  // Generate a new API key
  const generateApiKey = () => {
    const newKey = {
      id: `key-${apiKeys.length + 1}`,
      name: "New API Key",
      created: new Date().toISOString().split("T")[0],
      lastUsed: "-",
    };
    setApiKeys([...apiKeys, newKey]);
    toast.success("New API key generated successfully!");
  };

  // Delete an API key
  const deleteApiKey = (keyId: string) => {
    setApiKeys(apiKeys.filter((key) => key.id !== keyId));
    toast.success("API key deleted successfully");
  };

  // Reset account
  const resetAccount = () => {
    toast.success(
      "Account reset request submitted. You will receive further instructions by email."
    );
  };

  // Delete account
  const deleteAccount = () => {
    toast.success(
      "Account deletion initiated. You will receive a confirmation email."
    );
    setTimeout(() => {
      logout();
    }, 3000);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Profile & Settings</h1>
        <p className="text-muted-foreground">
          Manage your account preferences and settings
        </p>
      </div>

      <Tabs defaultValue="profile" className="space-y-4">
        <TabsList className="grid grid-cols-5 md:w-fit">
          <TabsTrigger value="profile">
            <User className="h-4 w-4 mr-2" />
            <span className="hidden md:inline">Profile</span>
          </TabsTrigger>
          <TabsTrigger value="notifications">
            <Bell className="h-4 w-4 mr-2" />
            <span className="hidden md:inline">Notifications</span>
          </TabsTrigger>
          <TabsTrigger value="preferences">
            <Settings className="h-4 w-4 mr-2" />
            <span className="hidden md:inline">Preferences</span>
          </TabsTrigger>
          <TabsTrigger value="api">
            <Key className="h-4 w-4 mr-2" />
            <span className="hidden md:inline">API Access</span>
          </TabsTrigger>
          <TabsTrigger value="danger">
            <Lock className="h-4 w-4 mr-2" />
            <span className="hidden md:inline">Account</span>
          </TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle>Personal Information</CardTitle>
              <CardDescription>
                Update your personal information and public profile
              </CardDescription>
            </CardHeader>
            <form onSubmit={handleSubmit}>
              <CardContent className="space-y-6">
                <div className="flex flex-col md:flex-row gap-6">
                  <div className="flex flex-col items-center space-y-2">
                    <Avatar className="w-24 h-24">
                      <AvatarImage src={`https://avatar.vercel.sh/${user?.name}`} />
                      <AvatarFallback>{user?.name.charAt(0)}</AvatarFallback>
                    </Avatar>
                    <Button variant="outline" size="sm">
                      Change Avatar
                    </Button>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="text-xs">
                        User
                      </Badge>
                      <Badge className="bg-primary/20 text-primary text-xs">
                        Pro Plan
                      </Badge>
                    </div>
                  </div>
                  <div className="flex-1 space-y-4">
                    <div className="grid gap-2">
                      <Label htmlFor="name">Full Name</Label>
                      <Input
                        id="name"
                        value={profileForm.name}
                        onChange={(e) =>
                          handleProfileChange("name", e.target.value)
                        }
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="email">Email Address</Label>
                      <Input
                        id="email"
                        type="email"
                        value={profileForm.email}
                        onChange={(e) =>
                          handleProfileChange("email", e.target.value)
                        }
                      />
                    </div>
                    
                    <IEEECredentialsSection />
                  </div>
                </div>

                <Separator />

                <div className="grid gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="bio">Bio</Label>
                    <Textarea
                      id="bio"
                      placeholder="Tell us a bit about yourself and your research interests"
                      value={profileForm.bio}
                      onChange={(e) =>
                        handleProfileChange("bio", e.target.value)
                      }
                      rows={4}
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="grid gap-2">
                      <Label htmlFor="institution">Institution</Label>
                      <Input
                        id="institution"
                        value={profileForm.institution}
                        onChange={(e) =>
                          handleProfileChange("institution", e.target.value)
                        }
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="role">Role</Label>
                      <Input
                        id="role"
                        value={profileForm.role}
                        onChange={(e) =>
                          handleProfileChange("role", e.target.value)
                        }
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="website">Website</Label>
                      <Input
                        id="website"
                        type="url"
                        value={profileForm.website}
                        onChange={(e) =>
                          handleProfileChange("website", e.target.value)
                        }
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button variant="outline" type="reset">
                  Cancel
                </Button>
                <Button type="submit">Save Changes</Button>
              </CardFooter>
            </form>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle>Notification Settings</CardTitle>
              <CardDescription>
                Configure how and when you receive notifications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <h3 className="font-medium">Email Notifications</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label htmlFor="email-notifications">
                        Email Notifications
                      </Label>
                      <p className="text-sm text-muted-foreground">
                        Receive email notifications (master toggle)
                      </p>
                    </div>
                    <Switch
                      id="email-notifications"
                      checked={notificationSettings.email}
                      onCheckedChange={(checked) =>
                        handleNotificationToggle("email", checked)
                      }
                    />
                  </div>
                  
                  <Separator className="my-4" />
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label>New Papers Added</Label>
                        <p className="text-sm text-muted-foreground">
                          Notify when papers are added to your library
                        </p>
                      </div>
                      <Switch
                        checked={notificationSettings.newPapers}
                        disabled={!notificationSettings.email}
                        onCheckedChange={(checked) =>
                          handleNotificationToggle("newPapers", checked)
                        }
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label>Analysis Completed</Label>
                        <p className="text-sm text-muted-foreground">
                          Notify when an analysis task is completed
                        </p>
                      </div>
                      <Switch
                        checked={notificationSettings.analysisCompleted}
                        disabled={!notificationSettings.email}
                        onCheckedChange={(checked) =>
                          handleNotificationToggle("analysisCompleted", checked)
                        }
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label>Weekly Research Digest</Label>
                        <p className="text-sm text-muted-foreground">
                          Weekly summary of your research activity
                        </p>
                      </div>
                      <Switch
                        checked={notificationSettings.weeklyDigest}
                        disabled={!notificationSettings.email}
                        onCheckedChange={(checked) =>
                          handleNotificationToggle("weeklyDigest", checked)
                        }
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label>Papers Related to Your Interests</Label>
                        <p className="text-sm text-muted-foreground">
                          Recommendations based on your research areas
                        </p>
                      </div>
                      <Switch
                        checked={notificationSettings.papersRelatedToYourInterests}
                        disabled={!notificationSettings.email}
                        onCheckedChange={(checked) =>
                          handleNotificationToggle(
                            "papersRelatedToYourInterests",
                            checked
                          )
                        }
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label>App Updates</Label>
                        <p className="text-sm text-muted-foreground">
                          New features and platform updates
                        </p>
                      </div>
                      <Switch
                        checked={notificationSettings.appUpdates}
                        disabled={!notificationSettings.email}
                        onCheckedChange={(checked) =>
                          handleNotificationToggle("appUpdates", checked)
                        }
                      />
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button onClick={() => toast.success("Notification settings saved")}>
                Save Preferences
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>

        {/* Preferences Tab */}
        <TabsContent value="preferences">
          <Card>
            <CardHeader>
              <CardTitle>User Preferences</CardTitle>
              <CardDescription>
                Customize your app experience and display preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="theme">Theme</Label>
                  <Select
                    value={preferences.theme}
                    onValueChange={(value) => handlePreferenceChange("theme", value)}
                  >
                    <SelectTrigger id="theme">
                      <SelectValue placeholder="Select theme" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="light">Light</SelectItem>
                      <SelectItem value="dark">Dark</SelectItem>
                      <SelectItem value="system">System</SelectItem>
                      <SelectItem value="academic">Academic</SelectItem>
                      <SelectItem value="high-contrast">High Contrast</SelectItem>
                      <SelectItem value="sepia">Sepia</SelectItem>
                      <SelectItem value="ocean-blue">Ocean Blue</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="language">Language</Label>
                  <Select
                    value={preferences.language}
                    onValueChange={(value) => handlePreferenceChange("language", value)}
                  >
                    <SelectTrigger id="language">
                      <SelectValue placeholder="Select language" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="english">English</SelectItem>
                      <SelectItem value="spanish">Spanish</SelectItem>
                      <SelectItem value="french">French</SelectItem>
                      <SelectItem value="german">German</SelectItem>
                      <SelectItem value="chinese">Chinese</SelectItem>
                      <SelectItem value="japanese">Japanese</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="paperDisplay">Paper Display</Label>
                  <Select
                    value={preferences.paperDisplay}
                    onValueChange={(value) =>
                      handlePreferenceChange("paperDisplay", value)
                    }
                  >
                    <SelectTrigger id="paperDisplay">
                      <SelectValue placeholder="Select display mode" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="compact">Compact</SelectItem>
                      <SelectItem value="detailed">Detailed</SelectItem>
                      <SelectItem value="grid">Grid</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="aiSummarization">AI Summarization Level</Label>
                  <Select
                    value={preferences.aiSummarization}
                    onValueChange={(value) =>
                      handlePreferenceChange("aiSummarization", value)
                    }
                  >
                    <SelectTrigger id="aiSummarization">
                      <SelectValue placeholder="Select summarization level" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="brief">Brief</SelectItem>
                      <SelectItem value="detailed">Detailed</SelectItem>
                      <SelectItem value="comprehensive">Comprehensive</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="citationFormat">Default Citation Format</Label>
                  <Select
                    value={preferences.citationFormat}
                    onValueChange={(value) =>
                      handlePreferenceChange("citationFormat", value)
                    }
                  >
                    <SelectTrigger id="citationFormat">
                      <SelectValue placeholder="Select citation format" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="apa">APA</SelectItem>
                      <SelectItem value="mla">MLA</SelectItem>
                      <SelectItem value="chicago">Chicago</SelectItem>
                      <SelectItem value="harvard">Harvard</SelectItem>
                      <SelectItem value="ieee">IEEE</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button onClick={() => toast.success("Preferences saved successfully!")}>
                Save Preferences
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>

        {/* API Key Storage Tab */}
        <TabsContent value="api">
          <Card>
            <CardHeader>
              <CardTitle>API Key Storage</CardTitle>
              <CardDescription>
                Securely store and manage your API keys for various services
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Add new API key form */}
              <div className="border rounded-md p-4">
                <h3 className="font-medium mb-3">Add New API Key</h3>
                <div className="grid gap-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label htmlFor="service-name">Service Name</Label>
                      <Input id="service-name" placeholder="OpenAI, Hugging Face, etc." />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="service-type">Service Type</Label>
                      <Select defaultValue="ai">
                        <SelectTrigger id="service-type">
                          <SelectValue placeholder="Select service type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="ai">AI / ML</SelectItem>
                          <SelectItem value="research">Research Database</SelectItem>
                          <SelectItem value="storage">Storage</SelectItem>
                          <SelectItem value="analysis">Data Analysis</SelectItem>
                          <SelectItem value="other">Other</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  
                  <div className="grid gap-2">
                    <Label htmlFor="api-key">API Key</Label>
                    <div className="flex gap-2">
                      <Input id="api-key" type="password" placeholder="Enter your API key" className="flex-1" />
                      <Button variant="secondary" size="sm">
                        <Eye className="h-4 w-4 mr-2" /> Show
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Your API keys are encrypted and stored securely</p>
                  </div>
                  
                  <div className="grid gap-2">
                    <Label htmlFor="key-description">Description (Optional)</Label>
                    <Textarea 
                      id="key-description" 
                      placeholder="Add notes about what this key is used for or any usage limits"
                      rows={2}
                    />
                  </div>
                  
                  <Button className="w-full" onClick={() => toast.success("API key saved successfully")}>
                    <Plus className="h-4 w-4 mr-2" /> Save API Key
                  </Button>
                </div>
              </div>
              
              {/* Stored API keys */}
              <div>
                <h3 className="font-medium mb-3">Your Stored API Keys</h3>
                <div className="space-y-3">
                  {[
                    { id: 1, name: "OpenAI GPT-4", type: "AI / ML", added: "2023-10-15" },
                    { id: 2, name: "Google Scholar", type: "Research Database", added: "2023-11-03" },
                    { id: 3, name: "Semantic Scholar", type: "Research Database", added: "2024-01-22" }
                  ].map((key) => (
                    <div key={key.id} className="border rounded-md p-4 flex items-center justify-between">
                      <div>
                        <div className="font-medium">{key.name}</div>
                        <div className="text-sm text-muted-foreground flex space-x-4">
                          <span>Type: {key.type}</span>
                          <span>Added: {key.added}</span>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button variant="outline" size="sm" onClick={() => toast.success("API key copied to clipboard")}>
                          <Copy className="h-4 w-4 mr-2" /> Copy
                        </Button>
                        <Button variant="destructive" size="sm">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Account Tab */}
        <TabsContent value="danger">
          <Card>
            <CardHeader>
              <CardTitle>Account Management</CardTitle>
              <CardDescription>
                Manage your account security and data
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <h3 className="font-medium">Change Password</h3>
                <div className="grid gap-2">
                  <Label htmlFor="current-password">Current Password</Label>
                  <Input id="current-password" type="password" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="new-password">New Password</Label>
                  <Input id="new-password" type="password" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="confirm-password">Confirm New Password</Label>
                  <Input id="confirm-password" type="password" />
                </div>
                <Button
                  onClick={() => toast.success("Password changed successfully")}
                >
                  Update Password
                </Button>
              </div>

              <Separator />

              <div className="space-y-2">
                <h3 className="font-medium">Export Your Data</h3>
                <p className="text-sm text-muted-foreground">
                  Download a copy of all your data, including papers, annotations, and analysis results.
                </p>
                <Button
                  variant="outline"
                  onClick={() =>
                    toast.success("Data export initiated. You will receive an email when it's ready.")
                  }
                >
                  <Download className="mr-2 h-4 w-4" />
                  Export Data
                </Button>
              </div>

              <Separator />

              <div className="space-y-4">
                <h3 className="font-medium text-destructive">Danger Zone</h3>
                <div className="space-y-4">
                  <div>
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button variant="outline" className="border-destructive/50 text-destructive">
                          <RotateCcw className="mr-2 h-4 w-4" />
                          Reset Account
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                          <AlertDialogDescription>
                            This will reset all your preferences and data. This action cannot be undone.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction onClick={resetAccount}>
                            Continue
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                    <p className="text-xs text-muted-foreground mt-1">
                      Reset your account to default settings but keep your papers and analyses.
                    </p>
                  </div>

                  <div>
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button variant="destructive">
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete Account
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                          <AlertDialogDescription>
                            This will permanently delete your account and all associated data.
                            This action cannot be undone.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction
                            onClick={deleteAccount}
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                          >
                            Delete Account
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                    <p className="text-xs text-muted-foreground mt-1">
                      Permanently delete your account and all associated data.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}