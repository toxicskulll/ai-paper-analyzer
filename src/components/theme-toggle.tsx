import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Moon, Sun, Laptop, BookOpen, Eye, Coffee, Waves } from "lucide-react";
import { useTheme } from "@/components/theme-provider";

export function ThemeToggle() {
  const { setTheme } = useTheme();

  const themes = [
    {
      name: "Light",
      value: "light",
      icon: <Sun className="h-4 w-4" />,
    },
    {
      name: "Dark",
      value: "dark",
      icon: <Moon className="h-4 w-4" />,
    },
    {
      name: "System",
      value: "system",
      icon: <Laptop className="h-4 w-4" />,
    },
    {
      name: "Academic",
      value: "academic",
      icon: <BookOpen className="h-4 w-4" />,
    },
    {
      name: "High Contrast",
      value: "high-contrast",
      icon: <Eye className="h-4 w-4" />,
    },
    {
      name: "Sepia",
      value: "sepia",
      icon: <Coffee className="h-4 w-4" />,
    },
    {
      name: "Ocean Blue",
      value: "ocean-blue",
      icon: <Waves className="h-4 w-4" />,
    },
  ];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {themes.map((theme) => (
          <DropdownMenuItem
            key={theme.value}
            onClick={() => setTheme(theme.value)}
            className="flex items-center gap-2"
          >
            {theme.icon}
            <span>{theme.name}</span>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}