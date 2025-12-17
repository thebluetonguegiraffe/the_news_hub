"use client";

import { API_URL, DEFAULT_HEADERS } from "../config";

import { useState } from "react";
import { MessageSquare, Bot, Zap, Send, Brain, Search, Clock, MessageCircle, ExternalLink, AlignCenter, SquareArrowOutUpRight, Newspaper } from "lucide-react";
import NavigationBar from "../components/NavigationBar";
import Footer from "../components/Footer";
import { Article, getDaysFromDate } from "../components/Articles";
import { useLanguage } from "../contexts/LanguageContext";

import RobustImageComponent from "../components/RobustImage";

const HeroSection = ({
  onSearch,
}: {
  onSearch: (query: string) => void;
}) => {
  const { t } = useLanguage();
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = () => {
  if (!searchQuery.trim()) return;
  setIsSearching(true);
  onSearch(searchQuery);
  setSearchQuery("");
  setIsSearching(false);
};

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <section className="bg-gradient-to-br from-primary/10 to-secondary/10 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 bg-[#f7c873]/20 text-[#1a2238] px-4 py-2 rounded-full mb-6">
            <Bot className="w-4 h-4" />
            <span className="text-sm font-medium">Learn about everything</span>
          </div>
          <h1 className="text-4xl md:text-6xl font-bold text-foreground mb-6">
            {t("nav.ai-chatbot")}
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            Ask questions about any news topic and get intelligent, accurate answers powered by advanced AI technology.
          </p>
          
          {/* Search Section */}
          <div className="max-w-2xl mx-auto">
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <div className="relative flex-1 w-full max-w-lg">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about any news topic, current events, or breaking news..."
                  className="w-full pl-10 pr-4 py-3 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  disabled={isSearching}
                />
              </div>
              <button
                onClick={handleSearch}
                disabled={!searchQuery.trim() || isSearching}
                className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isSearching ? (
                  <>
                    <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin"></div>
                    Searching...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Ask AI
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

const SearchResults = ({ query, summary, articles, isLoading }: { query: string; summary:string, articles: Article[]; isLoading: boolean }) => {
  if (!query) return null;

  if (isLoading) {
    return (
      <section className="py-16 bg-muted/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-full mb-6">
              <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            </div>
            <h2 className="text-3xl font-bold text-foreground mb-4">
              Searching for "{query}"...
            </h2>
            <p className="text-muted-foreground text-lg">
              Our AI is analyzing the latest news and finding the most relevant articles for you
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3].map((index) => (
              <div key={index} className="bg-card border border-border rounded-lg overflow-hidden shadow-lg animate-pulse">
                <div className="aspect-video bg-muted"></div>
                <div className="p-6">
                  <div className="h-4 bg-muted rounded mb-3"></div>
                  <div className="h-6 bg-muted rounded mb-3"></div>
                  <div className="h-4 bg-muted rounded mb-2"></div>
                  <div className="h-4 bg-muted rounded mb-4 w-3/4"></div>
                  <div className="h-4 bg-muted rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  }

  const [imageErrors, setImageErrors] = useState<{ [key: number]: boolean }>({});
  const handleImageError = (id: number) => {
    setImageErrors(prev => ({ ...prev, [id]: true }));
  };

  if (articles.length === 0) return null;

  return (
    <section className="py-16 bg-muted/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-foreground px-4 py-2 mb-4">
            Search Results for "{query}"
          </h2>

          {/* Summary */}
          <div className="inline-flex items-center gap-2 bg-[#f7c873]/20 text-[#1a2238] px-4 py-2 rounded-full mb-6">
            <AlignCenter className="w-4 h-4" />
            <span className="text-md font-medium">Summary</span>
          </div>

          <p className="text-muted-foreground text-lg px-4 py-2">
            {summary}
          </p>

          {/* Linked News */}
          <div className="inline-flex items-center gap-2 bg-[#f7c873]/20 text-[#1a2238] px-4 py-2 rounded-full mt-6 sm:mt-8 lg:mt-10 mb-6">
            <SquareArrowOutUpRight className="w-4 h-4" />
            <span className="text-md font-medium">Linked News</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {articles.map((article) => (
            <div key={article.id} className="bg-card border border-border rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition-shadow">
              <div className="aspect-video relative overflow-hidden"  >
                {imageErrors[article.id] ? (
                    <div className="w-full h-full bg-gradient-to-br from-[#f7c873]/20 to-[#f7c873]/10 flex items-center justify-center">
                      <Newspaper className="w-12 h-12 text-[#f7c873]" />
                    </div>
                  ) : (
                  <RobustImageComponent
                    images={article.image}
                    alt={article.title}
                    className="w-full h-full object-cover"
                    fallback={
                      <div className="w-full h-full bg-gradient-to-br from-[#f7c873]/20 to-[#f7c873]/10 flex items-center justify-center">
                        <Newspaper className="w-12 h-12 text-[#f7c873]" />
                      </div>
                    }
                  />
                )}
                <div className="absolute top-4 left-4">
                  <span className="px-3 py-1 bg-[#f7c873] text-[#1a2238] text-xs font-semibold rounded-full">
                    {article.topic}
                  </span>
                </div>
              </div>
              
              <div className="p-6">
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-3">
                  <Clock className="w-4 h-4" />
                  {getDaysFromDate(article.date)}
                </div>
                
                <h3 className="text-xl font-semibold text-foreground mb-3 line-clamp-2">
                  {article.title}
                </h3>
                
                <p className="text-muted-foreground mb-4 line-clamp-3">
                  {article.excerpt}
                </p>
                
                <a 
                  href={article.url}
                  className="inline-flex items-center gap-2 text-primary hover:text-primary/80 transition-colors font-medium"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Read More
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

const HowItWorksSection = () => {
  const { t } = useLanguage();
  
  const steps = [
    {
      icon: MessageSquare,
      title: "Ask Questions",
      description: "Simply type your question about any news topic or current event."
    },
    {
      icon: Brain,
      title: "AI Analysis",
      description: "Our advanced AI analyzes the latest information and provides comprehensive answers."
    },
    {
      icon: Zap,
      title: "Get Answers",
      description: "Receive accurate, up-to-date responses with relevant context and sources."
    }
  ];

  return (
    <section className="py-16 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-foreground mb-4">
            How It Works
          </h2>
          <p className="text-muted-foreground text-lg">
            Get intelligent answers to your news questions in three simple steps
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <div key={index} className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 text-primary rounded-full mb-4">
                <step.icon className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-2">{step.title}</h3>
              <p className="text-muted-foreground">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

const FAQSection = () => {
  const { t } = useLanguage();
  
  const faqs = [
    {
      question: "How accurate is the AI's information?",
      answer: "Our AI is trained on reliable news sources and provides information based on the latest verified reports. It always cites sources and indicates when information is preliminary."
    },
    {
      question: "Can I ask about any news topic?",
      answer: "Yes! You can ask about any current event, breaking news, political developments, scientific discoveries, business news, or any other topic that's in the news."
    },
    {
      question: "How does the AI stay updated?",
      answer: "Our AI continuously monitors and analyzes news from thousands of reliable sources, ensuring it has access to the most current information available."
    },
    {
      question: "Is my conversation private?",
      answer: "Yes, your conversations with the AI are private and not shared with third parties. We prioritize user privacy and data security."
    }
  ];

  return (
    <section className="py-16 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-[#f7c873]/20 rounded-full mb-6">
            <MessageCircle className="w-8 h-8 text-[#f7c873]" />
          </div>
          <h2 className="text-3xl font-bold text-foreground mb-4">
            {t("faq.title")}
          </h2>
          <p className="text-muted-foreground text-lg">
            {t("faq.subtitle")}
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {faqs.map((faq, index) => (
            <div key={index} className="bg-card border border-border rounded-lg p-6 hover:border-[#f7c873] transition-colors group">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-8 h-8 bg-[#f7c873]/20 rounded-full flex items-center justify-center group-hover:bg-[#f7c873] transition-colors">
                  <span className="text-[#1a2238] group-hover:text-[#1a2238] font-bold text-sm transition-colors">
                    {index + 1}
                  </span>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-foreground mb-2">
                    {faq.question}
                  </h3>
                  <p className="text-muted-foreground">{faq.answer}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default function AIPage() {
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [articles, setArticles] = useState<Article[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [summary, setSummary] = useState("");

  const handleSearch = async (query: string) => {
      setSearchQuery(query);
      setArticles([]);
      setIsLoading(true);

      try {
        const response = await fetch(`${API_URL}/ask_hub/`, {
          method: "POST",
          headers: DEFAULT_HEADERS,
          body: JSON.stringify({ question: query }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        const transformedArticles = data.articles.map((item: any) => ({
          id: item.id,
          title: item.metadata.title,
          excerpt: item.metadata.excerpt,
          topic: item.metadata.topic,
          source: item.metadata.source,
          date: item.metadata.published_date,
          image: item.metadata.image?.split(',').map((url: string) => url.trim()) || [], 
          url: item.metadata.url
        }));

        setArticles(transformedArticles || []);
        setSummary(data.summary || "No summary available for this query.");

      } catch (error) {
        console.error("Error fetching search results:", error);
      } finally {
        setIsLoading(false);
      }
    };

  return (
    <div className="min-h-screen bg-background">
      <NavigationBar activePage="ia" />
      <HeroSection onSearch={handleSearch} />
      <SearchResults query={searchQuery} summary={summary} articles={articles} isLoading={isLoading} />
      <HowItWorksSection />
      <FAQSection />
      <Footer />
    </div>
  );
} 