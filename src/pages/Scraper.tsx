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
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
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
import {
  Search,
  Filter,
  ArrowDown,
  Plus,
  Trash2,
  FileDown,
  FileCheck,
  BookOpen,
  FileQuestion,
  Download,
  Eye,
  ExternalLink,
} from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsContent, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Progress } from "@/components/ui/progress";

// Mock sources for academic papers
const paperSources = [
  { id: "arxiv", name: "arXiv" },
  { id: "ieee", name: "IEEE Xplore" },
  { id: "acm", name: "ACM Digital Library" },
  { id: "science_direct", name: "Science Direct" },
  { id: "springer", name: "Springer Link" },
  { id: "pubmed", name: "PubMed" },
];

// Mock data for search results
const mockSearchResults = [
  {
    id: "paper1",
    title:
      "Transformer-based Models for Natural Language Processing: A Comprehensive Review",
    authors: "Johnson, A., Smith, B., Williams, C.",
    source: "arXiv",
    year: 2023,
    abstract:
      "This review provides a comprehensive analysis of transformer-based models in natural language processing. It covers the evolution of these models from the original Transformer to state-of-the-art architectures, examining their strengths, limitations, and applications across various NLP tasks.",
    keywords: ["Transformers", "NLP", "Deep Learning", "Language Models"],
    citations: 87,
    url: "https://arxiv.org/abs/2305.12345",
    downloadAvailable: true,
  },
  {
    id: "paper2",
    title: "Quantum Machine Learning Algorithms: Current Status and Future Directions",
    authors: "Chen, L., Garcia, M., Rodriguez, P., Kumar, S.",
    source: "IEEE Xplore",
    year: 2022,
    abstract:
      "Quantum computing offers the potential to revolutionize machine learning algorithms by providing exponential speedups for certain computational tasks. This paper surveys the current landscape of quantum machine learning algorithms, analyzing their theoretical foundations, experimental implementations, and practical challenges.",
    keywords: [
      "Quantum Computing",
      "Machine Learning",
      "Quantum Algorithms",
      "Quantum Neural Networks",
    ],
    citations: 34,
    url: "https://ieeexplore.ieee.org/document/9876543",
    downloadAvailable: true,
  },
  {
    id: "paper3",
    title: "Climate Change Effects on Marine Biodiversity: A Meta-analysis",
    authors: "Thompson, E., Brown, J., Wilson, H.",
    source: "Science Direct",
    year: 2023,
    abstract:
      "This meta-analysis examines the impacts of climate change on marine biodiversity across different oceanic regions. By synthesizing data from 145 studies over the past 25 years, we identify key patterns of biodiversity loss, species migration, and ecosystem disruption attributable to rising ocean temperatures and acidification.",
    keywords: [
      "Climate Change",
      "Marine Biology",
      "Biodiversity",
      "Meta-analysis",
      "Ocean Ecosystems",
    ],
    citations: 12,
    url: "https://www.sciencedirect.com/science/article/pii/S0123456789",
    downloadAvailable: true,
  },
  {
    id: "paper4",
    title:
      "Ethical Considerations in AI-driven Healthcare Decision Support Systems",
    authors: "Davis, R., Jackson, K., Martinez, L., Taylor, N.",
    source: "ACM Digital Library",
    year: 2023,
    abstract:
      "As artificial intelligence increasingly informs healthcare decisions, ethical considerations become paramount. This paper examines the ethical implications of AI-driven healthcare decision support systems, focusing on issues of transparency, bias, privacy, informed consent, and professional responsibility.",
    keywords: [
      "AI Ethics",
      "Healthcare",
      "Decision Support Systems",
      "Medical AI",
    ],
    citations: 8,
    url: "https://dl.acm.org/doi/10.1145/1234567.1234568",
    downloadAvailable: false,
  },
  {
    id: "paper5",
    title:
      "Sustainable Energy Storage Systems for Renewable Integration: A Comparative Analysis",
    authors: "Lee, S., Patel, R., Anderson, M.",
    source: "Springer Link",
    year: 2022,
    abstract:
      "This study compares various energy storage technologies for their effectiveness in facilitating renewable energy integration. We evaluate battery, hydrogen, pumped hydro, and thermal storage systems across multiple metrics including efficiency, cost, lifespan, environmental impact, and grid compatibility.",
    keywords: [
      "Energy Storage",
      "Renewable Energy",
      "Sustainability",
      "Grid Integration",
    ],
    citations: 45,
    url: "https://link.springer.com/article/10.1007/s12345-678-9012-3",
    downloadAvailable: true,
  },
];

export default function Scraper() {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchFilters, setSearchFilters] = useState({
    sources: [] as string[],
    yearFrom: "2020",
    yearTo: "2023",
    openAccessOnly: false,
  });
  const [searchResults, setSearchResults] = useState<typeof mockSearchResults>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchCompleted, setSearchCompleted] = useState(false);
  const [selectedPapers, setSelectedPapers] = useState<string[]>([]);
  const [filterDialogOpen, setFilterDialogOpen] = useState(false);
  const [bulkDownloadDialogOpen, setBulkDownloadDialogOpen] = useState(false);
  const [downloadingPapers, setDownloadingPapers] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);
  const [previewPaper, setPreviewPaper] = useState<(typeof mockSearchResults)[0] | null>(null);

  // Handle search submission
  const handleSearch = () => {
    if (!searchQuery.trim()) {
      toast.error("Please enter a search query");
      return;
    }

    setIsSearching(true);
    setSearchCompleted(false);
    setSelectedPapers([]);

    // Simulate API call with timeout
    setTimeout(() => {
      setSearchResults(mockSearchResults);
      setIsSearching(false);
      setSearchCompleted(true);
      toast.success(`Found ${mockSearchResults.length} papers matching your search`);
    }, 2000);
  };

  // Toggle selection of a paper
  const togglePaperSelection = (paperId: string) => {
    setSelectedPapers((prev) =>
      prev.includes(paperId)
        ? prev.filter((id) => id !== paperId)
        : [...prev, paperId]
    );
  };

  // Handle filter changes
  const handleFilterChange = (key: string, value: boolean | string) => {
    setSearchFilters((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  // Toggle source selection in filters
  const toggleSource = (sourceId: string) => {
    setSearchFilters((prev) => ({
      ...prev,
      sources: prev.sources.includes(sourceId)
        ? prev.sources.filter((id) => id !== sourceId)
        : [...prev.sources, sourceId],
    }));
  };

  // Apply filters
  const applyFilters = () => {
    // In a real app, this would trigger a new search with the filters
    setFilterDialogOpen(false);
    toast.success("Filters applied to search");
    // For this demo, we'll just pretend the results were filtered
  };

  // Simulate downloading selected papers
  const downloadSelectedPapers = () => {
    setDownloadingPapers(true);
    setDownloadProgress(0);

    const totalSteps = selectedPapers.length;
    let currentStep = 0;

    const downloadInterval = setInterval(() => {
      currentStep += 1;
      const progress = Math.round((currentStep / totalSteps) * 100);
      setDownloadProgress(progress);

      if (currentStep === totalSteps) {
        clearInterval(downloadInterval);
        setDownloadingPapers(false);
        setBulkDownloadDialogOpen(false);
        toast.success(`Downloaded ${selectedPapers.length} papers to your library`);
        setSelectedPapers([]);
      }
    }, 1000);
  };

  // Open preview dialog for a paper
  const openPreview = (paper: (typeof mockSearchResults)[0]) => {
    setPreviewPaper(paper);
    setPreviewDialogOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Paper Scraper</h1>
        <p className="text-muted-foreground">
          Search and download research papers from multiple academic sources
        </p>
      </div>

      {/* Search bar */}
      <Card>
        <CardHeader>
          <CardTitle>Search for Papers</CardTitle>
          <CardDescription>
            Enter keywords, authors, titles, or research topics
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col gap-4 md:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                type="search"
                placeholder="e.g., machine learning, climate change, quantum computing..."
                className="pl-8 pr-4"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleSearch();
                }}
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setFilterDialogOpen(true)}
              >
                <Filter className="mr-2 h-4 w-4" />
                Filters
                {searchFilters.sources.length > 0 && (
                  <Badge className="ml-2" variant="secondary">
                    {searchFilters.sources.length}
                  </Badge>
                )}
              </Button>
              <Button onClick={handleSearch} disabled={isSearching}>
                {isSearching ? (
                  <>
                    <svg
                      className="animate-spin -ml-1 mr-2 h-4 w-4"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="mr-2 h-4 w-4" />
                    Search
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Search results */}
      {searchCompleted && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">
              Search Results{" "}
              <span className="text-muted-foreground">
                ({searchResults.length})
              </span>
            </h2>
            <div className="flex items-center gap-2">
              {selectedPapers.length > 0 && (
                <Button
                  variant="outline"
                  onClick={() => setBulkDownloadDialogOpen(true)}
                >
                  <Download className="mr-2 h-4 w-4" />
                  Download {selectedPapers.length} Selected
                </Button>
              )}
              <Select defaultValue="relevance">
                <SelectTrigger className="w-[160px]">
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="relevance">Relevance</SelectItem>
                  <SelectItem value="date-desc">Newest First</SelectItem>
                  <SelectItem value="date-asc">Oldest First</SelectItem>
                  <SelectItem value="citations-desc">Most Cited</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-4">
            {searchResults.map((paper) => (
              <Card key={paper.id} className="overflow-hidden">
                <div className="flex border-l-4 border-l-primary/70 h-full">
                  <div className="flex items-center pl-4">
                    <Checkbox
                      checked={selectedPapers.includes(paper.id)}
                      onCheckedChange={() => togglePaperSelection(paper.id)}
                    />
                  </div>
                  <div className="flex-1 p-4">
                    <div className="flex flex-col gap-2">
                      <div className="flex justify-between">
                        <h3 className="font-semibold text-lg">{paper.title}</h3>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => openPreview(paper)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            asChild
                          >
                            <a
                              href={paper.url}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              <ExternalLink className="h-4 w-4" />
                            </a>
                          </Button>
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {paper.authors} • {paper.source} • {paper.year} •{" "}
                        {paper.citations} citations
                      </p>
                      <p className="text-sm line-clamp-2">{paper.abstract}</p>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {paper.keywords.map((keyword: string) => (
                          <Badge
                            key={keyword}
                            variant="secondary"
                            className="text-xs font-normal"
                          >
                            {keyword}
                          </Badge>
                        ))}
                      </div>
                      <div className="flex justify-between items-center mt-2">
                        <div className="flex items-center gap-2">
                          {paper.downloadAvailable ? (
                            <Badge className="bg-green-500/20 text-green-700 dark:text-green-500 hover:bg-green-500/20">
                              <FileCheck className="mr-1 h-3 w-3" />
                              Full text available
                            </Badge>
                          ) : (
                            <Badge
                              variant="outline"
                              className="text-muted-foreground"
                            >
                              <FileQuestion className="mr-1 h-3 w-3" />
                              Abstract only
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() =>
                              toast.success(
                                `Added "${paper.title}" to your library`
                              )
                            }
                          >
                            <BookOpen className="mr-1 h-4 w-4" />
                            Add to Library
                          </Button>
                          {paper.downloadAvailable && (
                            <Button
                              size="sm"
                              onClick={() =>
                                toast.success(
                                  `Downloaded "${paper.title}" successfully`
                                )
                              }
                            >
                              <FileDown className="mr-1 h-4 w-4" />
                              Download
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Filter dialog */}
      <Dialog
        open={filterDialogOpen}
        onOpenChange={setFilterDialogOpen}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Search Filters</DialogTitle>
            <DialogDescription>
              Refine your search results with these filters
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-6 py-4">
            <div className="space-y-2">
              <h3 className="font-medium text-sm">Sources</h3>
              <div className="grid grid-cols-2 gap-2">
                {paperSources.map((source) => (
                  <div
                    key={source.id}
                    className="flex items-center space-x-2"
                  >
                    <Checkbox
                      id={`source-${source.id}`}
                      checked={searchFilters.sources.includes(source.id)}
                      onCheckedChange={() => toggleSource(source.id)}
                    />
                    <Label
                      htmlFor={`source-${source.id}`}
                      className="cursor-pointer"
                    >
                      {source.name}
                    </Label>
                  </div>
                ))}
              </div>
            </div>
            <Separator />
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="yearFrom">Year From</Label>
                <Select
                  value={searchFilters.yearFrom}
                  onValueChange={(value) =>
                    handleFilterChange("yearFrom", value)
                  }
                >
                  <SelectTrigger id="yearFrom">
                    <SelectValue placeholder="From Year" />
                  </SelectTrigger>
                  <SelectContent>
                    {Array.from({ length: 24 }, (_, i) => 2000 + i).map(
                      (year) => (
                        <SelectItem key={year} value={year.toString()}>
                          {year}
                        </SelectItem>
                      )
                    )}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="yearTo">Year To</Label>
                <Select
                  value={searchFilters.yearTo}
                  onValueChange={(value) =>
                    handleFilterChange("yearTo", value)
                  }
                >
                  <SelectTrigger id="yearTo">
                    <SelectValue placeholder="To Year" />
                  </SelectTrigger>
                  <SelectContent>
                    {Array.from({ length: 24 }, (_, i) => 2000 + i).map(
                      (year) => (
                        <SelectItem key={year} value={year.toString()}>
                          {year}
                        </SelectItem>
                      )
                    )}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <Separator />
            <div className="flex items-center space-x-2">
              <Checkbox
                id="openAccessOnly"
                checked={searchFilters.openAccessOnly}
                onCheckedChange={(checked) =>
                  handleFilterChange("openAccessOnly", checked)
                }
              />
              <Label htmlFor="openAccessOnly" className="cursor-pointer">
                Show only open access papers
              </Label>
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setFilterDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={applyFilters}>Apply Filters</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Bulk download dialog */}
      <AlertDialog
        open={bulkDownloadDialogOpen}
        onOpenChange={setBulkDownloadDialogOpen}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              Download {selectedPapers.length} Papers
            </AlertDialogTitle>
            <AlertDialogDescription>
              Selected papers will be downloaded and added to your library for
              offline access.
            </AlertDialogDescription>
          </AlertDialogHeader>

          {downloadingPapers && (
            <div className="space-y-2 py-4">
              <Progress value={downloadProgress} />
              <p className="text-sm text-center text-muted-foreground">
                Downloading papers... {downloadProgress}%
              </p>
            </div>
          )}

          <AlertDialogFooter>
            <AlertDialogCancel disabled={downloadingPapers}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={downloadSelectedPapers}
              disabled={downloadingPapers}
            >
              {downloadingPapers ? "Downloading..." : "Download"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Paper preview dialog */}
      <Dialog open={previewDialogOpen} onOpenChange={setPreviewDialogOpen}>
        <DialogContent className="sm:max-w-3xl max-h-[80vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle className="line-clamp-2">
              {previewPaper?.title}
            </DialogTitle>
            <DialogDescription>
              {previewPaper?.authors} • {previewPaper?.source} • {previewPaper?.year}
            </DialogDescription>
          </DialogHeader>
          
          <Tabs defaultValue="abstract" className="flex-1 overflow-hidden flex flex-col">
            <TabsList>
              <TabsTrigger value="abstract">Abstract</TabsTrigger>
              <TabsTrigger value="details">Details</TabsTrigger>
            </TabsList>
            <TabsContent value="abstract" className="flex-1 overflow-hidden">
              <ScrollArea className="h-[40vh]">
                <div className="space-y-4 p-1">
                  <p>{previewPaper?.abstract}</p>
                  <div className="flex flex-wrap gap-2">
                    {previewPaper?.keywords.map((keyword: string) => (
                      <Badge
                        key={keyword}
                        variant="secondary"
                      >
                        {keyword}
                      </Badge>
                    ))}
                  </div>
                </div>
              </ScrollArea>
            </TabsContent>
            <TabsContent value="details" className="flex-1 overflow-hidden">
              <ScrollArea className="h-[40vh]">
                <div className="space-y-4 p-1">
                  <div>
                    <h3 className="font-medium">Source</h3>
                    <p className="text-sm text-muted-foreground">{previewPaper?.source}</p>
                  </div>
                  <div>
                    <h3 className="font-medium">Year</h3>
                    <p className="text-sm text-muted-foreground">{previewPaper?.year}</p>
                  </div>
                  <div>
                    <h3 className="font-medium">Citations</h3>
                    <p className="text-sm text-muted-foreground">{previewPaper?.citations}</p>
                  </div>
                  <div>
                    <h3 className="font-medium">URL</h3>
                    <a 
                      href={previewPaper?.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-sm text-primary hover:underline flex items-center"
                    >
                      {previewPaper?.url}
                      <ExternalLink className="ml-1 h-3 w-3" />
                    </a>
                  </div>
                </div>
              </ScrollArea>
            </TabsContent>
          </Tabs>

          <DialogFooter>
            <div className="flex w-full justify-between">
              <Button
                variant="outline"
                onClick={() =>
                  toast.success(
                    `Added "${previewPaper?.title}" to your library`
                  )
                }
              >
                <BookOpen className="mr-2 h-4 w-4" />
                Add to Library
              </Button>
              {previewPaper?.downloadAvailable && (
                <Button
                  onClick={() =>
                    toast.success(
                      `Downloaded "${previewPaper?.title}" successfully`
                    )
                  }
                >
                  <FileDown className="mr-2 h-4 w-4" />
                  Download PDF
                </Button>
              )}
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}