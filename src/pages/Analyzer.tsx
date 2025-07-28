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
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import {
  FileUp,
  Link as LinkIcon,
  FileText,
  Sparkles,
  Save,
  FileQuestion,
  BookOpen,
  Activity,
  Download,
  Clipboard,
  RotateCcw,
} from "lucide-react";
import { toast } from "sonner";

// Mock analysis results
const mockAnalysisResults = {
  summary:
    "This paper introduces a novel approach to natural language processing using transformer-based architectures. The authors demonstrate significant improvements in language understanding tasks compared to previous methods, with a 12% increase in accuracy on standard benchmarks. The work contributes both theoretical advances in attention mechanisms and practical implementations that could benefit a range of NLP applications.",
  keyFindings: [
    "Proposed a new transformer architecture with modified attention mechanisms",
    "Achieved 12% improvement on GLUE benchmark tasks compared to SOTA",
    "Introduced a more efficient training method requiring 30% less computational resources",
    "Demonstrated better performance in low-resource settings with limited training data",
    "Provided theoretical analysis of why their approach overcomes limitations in previous models",
  ],
  strengthsWeaknesses: {
    strengths: [
      "Novel technical contribution with clear innovation",
      "Comprehensive empirical evaluation across multiple datasets",
      "Strong theoretical foundation with mathematical proofs",
      "Code and models publicly available for reproducibility",
    ],
    weaknesses: [
      "Limited discussion of ethical implications",
      "Evaluation focused primarily on English language datasets",
      "Computational requirements still high for deployment in some settings",
      "Some comparisons to competing methods use different evaluation metrics",
    ],
  },
  relatedPapers: [
    {
      title: "Attention Is All You Need",
      authors: "Vaswani et al.",
      year: 2017,
      relevance:
        "Foundational paper that introduced the transformer architecture which this work builds upon",
    },
    {
      title: "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
      authors: "Devlin et al.",
      year: 2019,
      relevance:
        "Established the pre-training paradigm that influenced the current paper's approach",
    },
    {
      title: "RoBERTa: A Robustly Optimized BERT Pretraining Approach",
      authors: "Liu et al.",
      year: 2019,
      relevance:
        "Provided optimization techniques that the current paper compares against",
    },
  ],
  researchGaps: [
    "Applying the proposed methods to multilingual settings",
    "Exploring model compression techniques to reduce deployment costs",
    "Evaluating performance on domain-specific tasks beyond general NLP benchmarks",
    "Investigating the ethical implications and potential biases in the model",
  ],
};

export default function Analyzer() {
  const [inputMethod, setInputMethod] = useState("upload");
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState("");
  const [text, setText] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<typeof mockAnalysisResults | null>(null);

  // Handle file upload
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  // Handle analysis submission
  const handleAnalyze = () => {
    if (
      (inputMethod === "upload" && !file) ||
      (inputMethod === "url" && !url) ||
      (inputMethod === "text" && !text)
    ) {
      toast.error("Please provide input for analysis");
      return;
    }

    setIsAnalyzing(true);
    
    // Simulate API call with timeout
    setTimeout(() => {
      setIsAnalyzing(false);
      setAnalysisComplete(true);
      setAnalysisResults(mockAnalysisResults);
      toast.success("Analysis completed successfully!");
    }, 3000);
  };

  // Reset the analysis
  const resetAnalysis = () => {
    setFile(null);
    setUrl("");
    setText("");
    setAnalysisComplete(false);
    setAnalysisResults(null);
  };

  // Copy to clipboard function
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard!");
  };

  // Save to library function
  const saveToLibrary = () => {
    toast.success("Paper saved to your library!");
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Research Paper Analyzer</h1>
        <p className="text-muted-foreground">
          Upload, analyze, and extract insights from academic papers
        </p>
      </div>

      {!analysisComplete ? (
        <Card>
          <CardHeader>
            <CardTitle>Upload Paper for Analysis</CardTitle>
            <CardDescription>
              Provide a research paper for AI-powered analysis and insights
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs
              defaultValue="upload"
              value={inputMethod}
              onValueChange={setInputMethod}
              className="space-y-4"
            >
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="upload">
                  <FileUp className="mr-2 h-4 w-4" />
                  Upload File
                </TabsTrigger>
                <TabsTrigger value="url">
                  <LinkIcon className="mr-2 h-4 w-4" />
                  Paper URL
                </TabsTrigger>
                <TabsTrigger value="text">
                  <FileText className="mr-2 h-4 w-4" />
                  Paste Text
                </TabsTrigger>
              </TabsList>

              <TabsContent value="upload" className="space-y-4">
                <div className="grid w-full gap-2">
                  <Label htmlFor="file">Upload PDF or Document</Label>
                  <div className="flex items-center justify-center w-full">
                    <label
                      htmlFor="file-upload"
                      className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-md cursor-pointer bg-background hover:bg-secondary/50"
                    >
                      <div className="flex flex-col items-center justify-center pt-5 pb-6">
                        <FileUp className="w-8 h-8 text-muted-foreground mb-2" />
                        <p className="mb-2 text-sm text-muted-foreground">
                          <span className="font-medium">Click to upload</span> or
                          drag and drop
                        </p>
                        <p className="text-xs text-muted-foreground">
                          PDF, DOC, or DOCX (max. 20MB)
                        </p>
                      </div>
                      <input
                        id="file-upload"
                        name="file-upload"
                        type="file"
                        className="hidden"
                        accept=".pdf,.doc,.docx"
                        onChange={handleFileChange}
                      />
                    </label>
                  </div>
                  {file && (
                    <p className="text-sm text-muted-foreground">
                      Selected file: {file.name}
                    </p>
                  )}
                </div>
              </TabsContent>

              <TabsContent value="url" className="space-y-4">
                <div className="grid w-full gap-2">
                  <Label htmlFor="url">Paper URL</Label>
                  <Input
                    id="url"
                    placeholder="https://arxiv.org/pdf/1234.5678.pdf"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                  />
                  <p className="text-sm text-muted-foreground">
                    Enter the URL of a paper from sources like arXiv, IEEE, ACM,
                    or other academic repositories
                  </p>
                </div>
              </TabsContent>

              <TabsContent value="text" className="space-y-4">
                <div className="grid w-full gap-2">
                  <Label htmlFor="text">Paper Text</Label>
                  <Textarea
                    id="text"
                    placeholder="Paste the abstract or full text of the paper here..."
                    rows={10}
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                  />
                </div>
              </TabsContent>
            </Tabs>

            <div className="mt-6 space-y-4">
              <div className="grid w-full gap-2">
                <Label htmlFor="analysis-type">Analysis Type</Label>
                <Select defaultValue="comprehensive">
                  <SelectTrigger>
                    <SelectValue placeholder="Select analysis type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="comprehensive">
                      Comprehensive Analysis
                    </SelectItem>
                    <SelectItem value="summary">Summary Only</SelectItem>
                    <SelectItem value="critique">
                      Critical Evaluation
                    </SelectItem>
                    <SelectItem value="comparison">
                      Literature Comparison
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button variant="outline" onClick={resetAnalysis}>
              Reset
            </Button>
            <Button onClick={handleAnalyze} disabled={isAnalyzing}>
              {isAnalyzing ? (
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
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Analyze Paper
                </>
              )}
            </Button>
          </CardFooter>
        </Card>
      ) : (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold">Analysis Results</h2>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={resetAnalysis}>
                <RotateCcw className="mr-2 h-4 w-4" />
                New Analysis
              </Button>
              <Button variant="outline" size="sm" onClick={saveToLibrary}>
                <Save className="mr-2 h-4 w-4" />
                Save to Library
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() =>
                  copyToClipboard(JSON.stringify(analysisResults, null, 2))
                }
              >
                <Clipboard className="mr-2 h-4 w-4" />
                Copy All
              </Button>
              <Button variant="outline" size="sm">
                <Download className="mr-2 h-4 w-4" />
                Export
              </Button>
            </div>
          </div>

          <Tabs defaultValue="summary" className="space-y-4">
            <TabsList>
              <TabsTrigger value="summary">
                <BookOpen className="mr-2 h-4 w-4" />
                Summary
              </TabsTrigger>
              <TabsTrigger value="key-findings">
                <Sparkles className="mr-2 h-4 w-4" />
                Key Findings
              </TabsTrigger>
              <TabsTrigger value="evaluation">
                <Activity className="mr-2 h-4 w-4" />
                Critical Evaluation
              </TabsTrigger>
              <TabsTrigger value="related">
                <FileQuestion className="mr-2 h-4 w-4" />
                Related Work & Gaps
              </TabsTrigger>
            </TabsList>

            <TabsContent value="summary" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Executive Summary</CardTitle>
                  <CardDescription>
                    Concise overview of the paper's contributions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p>{analysisResults.summary}</p>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="key-findings" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Key Findings & Contributions</CardTitle>
                  <CardDescription>
                    Main discoveries and contributions of the paper
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 list-disc pl-5">
                    {analysisResults.keyFindings.map((finding: string, index: number) => (
                      <li key={index}>{finding}</li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="evaluation" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Strengths & Weaknesses</CardTitle>
                  <CardDescription>
                    Critical evaluation of the paper's merits and limitations
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-3">
                    <h3 className="font-medium text-lg">Strengths</h3>
                    <ul className="space-y-2 list-disc pl-5">
                      {analysisResults.strengthsWeaknesses.strengths.map(
                        (strength: string, index: number) => (
                          <li key={index}>{strength}</li>
                        )
                      )}
                    </ul>
                  </div>
                  <Separator />
                  <div className="space-y-3">
                    <h3 className="font-medium text-lg">Weaknesses</h3>
                    <ul className="space-y-2 list-disc pl-5">
                      {analysisResults.strengthsWeaknesses.weaknesses.map(
                        (weakness: string, index: number) => (
                          <li key={index}>{weakness}</li>
                        )
                      )}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="related" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Related Papers</CardTitle>
                  <CardDescription>
                    Important related work and connections
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {analysisResults.relatedPapers.map(
                      (paper: {title: string; authors: string; year: number; relevance: string}, index: number) => (
                        <div
                          key={index}
                          className="border rounded-md p-3 space-y-1"
                        >
                          <h4 className="font-medium">{paper.title}</h4>
                          <p className="text-sm text-muted-foreground">
                            {paper.authors} ({paper.year})
                          </p>
                          <p className="text-sm">{paper.relevance}</p>
                        </div>
                      )
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Research Gaps & Future Directions</CardTitle>
                  <CardDescription>
                    Opportunities for future research
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 list-disc pl-5">
                    {analysisResults.researchGaps.map(
                      (gap: string, index: number) => (
                        <li key={index}>{gap}</li>
                      )
                    )}
                  </ul>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      )}
    </div>
  );
}