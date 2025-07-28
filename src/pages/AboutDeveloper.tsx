import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Github, Linkedin, Mail, Twitter } from "lucide-react";

export default function AboutDeveloper() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">About Developer</h1>
        <p className="text-muted-foreground">
          Learn more about the creator of this application
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-1">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <Avatar className="w-24 h-24">
                <AvatarImage src="https://github.com/identicons/developer.png" />
                <AvatarFallback>Dev</AvatarFallback>
              </Avatar>
            </div>
            <CardTitle>AI/ML Engineer</CardTitle>
            <CardDescription>BMS Institute of Technology, Bangalore</CardDescription>
            
            <div className="flex justify-center mt-4 space-x-2">
              <Badge variant="outline" className="text-xs">
                AI/ML
              </Badge>
              <Badge variant="outline" className="text-xs">
                Research
              </Badge>
              <Badge variant="outline" className="text-xs">
                FullStack
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-center space-x-3">
              <Button variant="outline" size="icon">
                <Github className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon">
                <Linkedin className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon">
                <Twitter className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon">
                <Mail className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>About Me</CardTitle>
            <CardDescription>My journey and expertise</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p>
              I'm an AI/ML Engineer at BMS Institute of Technology in Bangalore, passionate about bridging the gap between academic research and practical applications in artificial intelligence.
            </p>
            
            <p>
              I specialize in natural language processing, machine learning, and developing tools that help researchers streamline their work. This Research Paper Analyzer is one of my passion projects aimed at helping fellow researchers and students quickly understand, analyze, and extract insights from academic papers.
            </p>
            
            <h3 className="text-lg font-semibold mt-6">Skills & Technologies</h3>
            <div className="flex flex-wrap gap-2 mt-2">
              <Badge>Python</Badge>
              <Badge>TensorFlow</Badge>
              <Badge>PyTorch</Badge>
              <Badge>NLP</Badge>
              <Badge>Computer Vision</Badge>
              <Badge>React</Badge>
              <Badge>TypeScript</Badge>
              <Badge>Node.js</Badge>
              <Badge>Research Methodology</Badge>
            </div>
            
            <h3 className="text-lg font-semibold mt-6">Projects</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li>AI Research Paper Analyzer Pro - A tool for academic paper analysis and management</li>
              <li>NLP-driven Citation Network Analysis System</li>
              <li>Automated Literature Review Assistant</li>
              <li>Research Topic Trend Forecasting Model</li>
            </ul>
            
            <h3 className="text-lg font-semibold mt-6">Education</h3>
            <p>B.E. Computer Science, BMS Institute of Technology</p>
            <p>M.Tech Artificial Intelligence, In Progress</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}