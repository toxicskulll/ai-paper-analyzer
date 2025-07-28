import { Toaster } from '@/components/ui/sonner';
import { TooltipProvider } from '@/components/ui/tooltip';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@/components/theme-provider';
import { AuthProvider } from '@/context/auth-context';
import Layout from '@/components/layout/layout';

// Pages
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import PaperScraper from './pages/PaperScraper';
import PaperLibrary from './pages/PaperLibrary';
import PaperAnalyzer from './pages/PaperAnalyzer';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import ActivityLog from './pages/ActivityLog';
import AboutDeveloper from './pages/AboutDeveloper';
import NotFound from './pages/NotFound';

// Admin Pages
import AdminLayout from './pages/admin/AdminLayout';
import AdminDashboard from './pages/admin/AdminDashboard';
import UserManagement from './pages/admin/UserManagement';
import LicenseManagement from './pages/admin/LicenseManagement';
import AuditLogs from './pages/admin/AuditLogs';
import Analytics from './pages/admin/Analytics';
import SystemSettings from './pages/admin/SystemSettings';

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider defaultTheme="system" storageKey="paper-analyzer-theme">
      <TooltipProvider>
        <Toaster />
        <BrowserRouter>
          <AuthProvider>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/admin-register" element={<Register />} />
              
              {/* Main User Routes */}
              <Route path="/" element={<Layout />}>
                <Route index element={<Navigate replace to="/dashboard" />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="scraper" element={<PaperScraper />} />
                <Route path="library" element={<PaperLibrary />} />
                <Route path="analyzer" element={<PaperAnalyzer />} />
                <Route path="profile" element={<Profile />} />
                <Route path="settings" element={<Settings />} />
                <Route path="activity" element={<ActivityLog />} />
                <Route path="about-developer" element={<AboutDeveloper />} />
              </Route>
              
              {/* Admin Routes */}
              <Route path="/admin" element={<AdminLayout />}>
                <Route index element={<Navigate replace to="/admin/dashboard" />} />
                <Route path="dashboard" element={<AdminDashboard />} />
                <Route path="users" element={<UserManagement />} />
                <Route path="licenses" element={<LicenseManagement />} />
                <Route path="audit" element={<AuditLogs />} />
                <Route path="analytics" element={<Analytics />} />
                <Route path="settings" element={<SystemSettings />} />
              </Route>
              
              <Route path="*" element={<NotFound />} />
            </Routes>
          </AuthProvider>
        </BrowserRouter>
      </TooltipProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;