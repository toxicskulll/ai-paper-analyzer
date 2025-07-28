import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { toast } from "sonner";
import {
  FileText,
  Search,
  Calendar,
  Tag,
  Users,
  MoreHorizontal,
  Star,
  StarOff,
  Trash2,
  BookOpen,
  Filter,
  ChevronDown,
} from "lucide-react";

// Mock data for the paper library
const mockPapers = [
  {
    id: 1,
    title: "Advances in Deep Learning: A Comprehensive Survey",
    authors: "Smith, J., Johnson, A., Williams, R.",
    journal: "Journal of Machine Learning Research",
    year: 2023,
    abstract:
      "This comprehensive survey examines recent advances in deep learning techniques, architectures, and applications across various domains.",
    keywords: ["Deep Learning", "Survey", "Neural Networks"],
    favorite: true,
    dateAdded: "2023-10-15",
  },
  {
    id: 2,
    title: "Quantum Computing: Present and Future",
    authors: "Chen, L., Brown, M., Garcia, S.",
    journal: "Nature Quantum Information",
    year: 2022,
    abstract:
      "An exploration of the current state of quantum computing technology and its potential future developments and applications.",
    keywords: ["Quantum Computing", "Qubits", "Quantum Algorithms"],
    favorite: false,
    dateAdded: "2023-09-22",
  },
  {
    id: 3,
    title: "Climate Change Effects on Marine Ecosystems",
    authors: "Roberts, E., Thompson, K., Davis, P.",
    journal: "Oceanography",
    year: 2023,
    abstract:
      "This paper analyzes the impact of climate change on various marine ecosystems, with a focus on coral reefs and coastal environments.",
    keywords: ["Climate Change", "Marine Biology", "Ecosystems"],
    favorite: false,
    dateAdded: "2023-11-05",
  },
  {
    id: 4,
    title: "Artificial Intelligence in Healthcare: Ethical Considerations",
    authors: "Wilson, H., Taylor, M., Anderson, J.",
    journal: "Journal of Medical Ethics",
    year: 2022,
    abstract:
      "An examination of ethical challenges arising from the implementation of AI technologies in healthcare settings.",
    keywords: ["AI Ethics", "Healthcare", "Medical Technology"],
    favorite: true,
    dateAdded: "2023-08-30",
  },
  {
    id: 5,
    title: "Advancements in Renewable Energy Storage",
    authors: "Patel, R., Kim, S., Gupta, A.",
    journal: "Renewable Energy",
    year: 2023,
    abstract:
      "This research presents recent innovations in energy storage technologies for renewable energy sources.",
    keywords: ["Renewable Energy", "Energy Storage", "Sustainability"],
    favorite: false,
    dateAdded: "2023-10-28",
  },
];

export default function Library() {
  const [papers, setPapers] = useState(mockPapers);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFilter, setSelectedFilter] = useState("all");
  const [selectedSort, setSelectedSort] = useState("date-desc");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [paperToDelete, setPaperToDelete] = useState<number | null>(null);
  
  // Multi-selection state
  const [selectedPapers, setSelectedPapers] = useState<number[]>([]);
  const [selectMode, setSelectMode] = useState(false);

  // Filter papers based on search and filters
  const filteredPapers = papers.filter((paper) => {
    // Search filter
    const searchMatch =
      paper.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      paper.authors.toLowerCase().includes(searchQuery.toLowerCase()) ||
      paper.abstract.toLowerCase().includes(searchQuery.toLowerCase()) ||
      paper.keywords.some((keyword) =>
        keyword.toLowerCase().includes(searchQuery.toLowerCase())
      );

    // Category filter
    if (selectedFilter === "all") return searchMatch;
    if (selectedFilter === "favorites") return searchMatch && paper.favorite;
    if (selectedFilter === "recent")
      return (
        searchMatch &&
        new Date(paper.dateAdded) >
          new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
      );

    return searchMatch;
  });

  // Sort papers
  const sortedPapers = [...filteredPapers].sort((a, b) => {
    switch (selectedSort) {
      case "date-desc":
        return new Date(b.dateAdded).getTime() - new Date(a.dateAdded).getTime();
      case "date-asc":
        return new Date(a.dateAdded).getTime() - new Date(b.dateAdded).getTime();
      case "title-asc":
        return a.title.localeCompare(b.title);
      case "title-desc":
        return b.title.localeCompare(a.title);
      case "year-desc":
        return b.year - a.year;
      case "year-asc":
        return a.year - b.year;
      default:
        return 0;
    }
  });

  // Toggle favorite status
  const toggleFavorite = (id: number) => {
    setPapers(
      papers.map((paper) =>
        paper.id === id ? { ...paper, favorite: !paper.favorite } : paper
      )
    );
  };

  // Multi-selection methods
  const togglePaperSelection = (id: number) => {
    setSelectedPapers(prev => 
      prev.includes(id) 
        ? prev.filter(paperId => paperId !== id) 
        : [...prev, id]
    );
  };

  const toggleSelectMode = () => {
    setSelectMode(prev => !prev);
    if (selectMode) {
      setSelectedPapers([]);
    }
  };

  const selectAll = () => {
    setSelectedPapers(sortedPapers.map(paper => paper.id));
  };

  const deselectAll = () => {
    setSelectedPapers([]);
  };

  const analyzeSelectedPapers = () => {
    if (selectedPapers.length === 0) {
      toast.error("Please select at least one paper to analyze");
      return;
    }
    
    const selectedPaperTitles = papers
      .filter(paper => selectedPapers.includes(paper.id))
      .map(paper => paper.title);
    
    toast.success(`Analyzing ${selectedPapers.length} papers`);
    console.log("Papers to analyze:", selectedPaperTitles);
    // In a real implementation, this would navigate to the analyzer page
    // with the selected papers as parameters
  };

  // Delete paper
  const deletePaper = () => {
    if (paperToDelete !== null) {
      setPapers(papers.filter((paper) => paper.id !== paperToDelete));
      setPaperToDelete(null);
      setDeleteDialogOpen(false);
    }
  };

  // Delete multiple papers
  const deleteSelectedPapers = () => {
    if (selectedPapers.length > 0) {
      setPapers(papers.filter((paper) => !selectedPapers.includes(paper.id)));
      setSelectedPapers([]);
      toast.success(`${selectedPapers.length} papers deleted`);
    }
  };

  // Confirmation dialog for delete
  const openDeleteDialog = (id: number) => {
    setPaperToDelete(id);
    setDeleteDialogOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Research Paper Library</h1>
        <p className="text-muted-foreground">
          Manage and organize your research papers
        </p>
      </div>

      {/* Search and filters */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search papers by title, author, or keyword..."
            className="pl-8 w-full"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={selectMode ? "secondary" : "outline"}
            size="sm"
            onClick={toggleSelectMode}
            className="flex items-center"
          >
            <Checkbox 
              checked={selectMode}
              className="mr-2 h-4 w-4"
            />
            Select
          </Button>

          <Select value={selectedFilter} onValueChange={setSelectedFilter}>
            <SelectTrigger className="w-[160px]">
              <Filter className="mr-2 h-4 w-4" />
              <SelectValue placeholder="Filter" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Papers</SelectItem>
              <SelectItem value="favorites">Favorites</SelectItem>
              <SelectItem value="recent">Recent (30 days)</SelectItem>
            </SelectContent>
          </Select>
          <Select value={selectedSort} onValueChange={setSelectedSort}>
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="date-desc">Newest First</SelectItem>
              <SelectItem value="date-asc">Oldest First</SelectItem>
              <SelectItem value="title-asc">Title (A-Z)</SelectItem>
              <SelectItem value="title-desc">Title (Z-A)</SelectItem>
              <SelectItem value="year-desc">Year (Newest)</SelectItem>
              <SelectItem value="year-asc">Year (Oldest)</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Multi-select actions */}
      {selectMode && (
        <div className="flex items-center gap-2 p-2 bg-muted/30 rounded-lg">
          <span className="text-sm font-medium ml-2">
            {selectedPapers.length} papers selected
          </span>
          <div className="ml-auto flex items-center gap-2">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={selectAll}
              disabled={sortedPapers.length === 0}
            >
              Select All
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={deselectAll}
              disabled={selectedPapers.length === 0}
            >
              Deselect All
            </Button>
            <Button 
              variant="default" 
              size="sm" 
              onClick={analyzeSelectedPapers}
              disabled={selectedPapers.length === 0}
            >
              Analyze Selected
            </Button>
            <Button 
              variant="destructive" 
              size="sm" 
              onClick={deleteSelectedPapers}
              disabled={selectedPapers.length === 0}
            >
              Delete Selected
            </Button>
          </div>
        </div>
      )}

      {/* Paper grid */}
      {sortedPapers.length === 0 ? (
        <div className="flex flex-col items-center justify-center border rounded-lg p-8">
          <BookOpen className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium">No papers found</h3>
          <p className="text-sm text-muted-foreground text-center mt-1">
            Try adjusting your search or filters, or add new papers to your library.
          </p>
          <Button className="mt-4">Add Papers</Button>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {sortedPapers.map((paper) => (
            <Card 
              key={paper.id}
              className={selectedPapers.includes(paper.id) ? "border-primary ring-1 ring-primary" : ""}
            >
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    {selectMode && (
                      <Checkbox 
                        checked={selectedPapers.includes(paper.id)}
                        onCheckedChange={() => togglePaperSelection(paper.id)}
                        className="mt-1"
                      />
                    )}
                    <div>
                      <CardTitle className="line-clamp-2">{paper.title}</CardTitle>
                      <CardDescription className="mt-1">
                        {paper.authors}
                      </CardDescription>
                    </div>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuLabel>Actions</DropdownMenuLabel>
                      <DropdownMenuSeparator />
                      {selectMode ? (
                        <DropdownMenuItem
                          onClick={() => togglePaperSelection(paper.id)}
                        >
                          <Checkbox 
                            checked={selectedPapers.includes(paper.id)}
                            className="mr-2 h-4 w-4"
                          />
                          {selectedPapers.includes(paper.id) ? "Deselect" : "Select"}
                        </DropdownMenuItem>
                      ) : null}
                      <DropdownMenuItem
                        onClick={() => toggleFavorite(paper.id)}
                      >
                        {paper.favorite ? (
                          <>
                            <StarOff className="mr-2 h-4 w-4" /> Remove from favorites
                          </>
                        ) : (
                          <>
                            <Star className="mr-2 h-4 w-4" /> Add to favorites
                          </>
                        )}
                      </DropdownMenuItem>
                      <DropdownMenuItem asChild>
                        <a href="/analyzer">
                          <FileText className="mr-2 h-4 w-4" /> Analyze paper
                        </a>
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onClick={() => openDeleteDialog(paper.id)}
                        className="text-destructive focus:text-destructive"
                      >
                        <Trash2 className="mr-2 h-4 w-4" /> Delete paper
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </CardHeader>
              <CardContent className="pb-2">
                <ScrollArea className="h-20">
                  <p className="text-sm text-muted-foreground">{paper.abstract}</p>
                </ScrollArea>
                <div className="flex flex-wrap gap-2 mt-3">
                  {paper.keywords.map((keyword) => (
                    <Badge
                      key={keyword}
                      variant="secondary"
                      className="text-xs font-normal"
                    >
                      {keyword}
                    </Badge>
                  ))}
                </div>
              </CardContent>
              <CardFooter className="pt-2 flex justify-between text-xs text-muted-foreground">
                <div className="flex items-center">
                  <Users className="mr-1 h-3 w-3" />
                  <span>{paper.journal}</span>
                </div>
                <div className="flex items-center">
                  <Calendar className="mr-1 h-3 w-3" />
                  <span>{paper.year}</span>
                </div>
                {paper.favorite && (
                  <div>
                    <Star className="h-3 w-3 text-yellow-500" />
                  </div>
                )}
              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      {/* Delete confirmation dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete this paper from your library. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={deletePaper}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}