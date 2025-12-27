"use client";

import { API_URL, DEFAULT_HEADERS } from "../config";

import { useState } from "react";
import { MessageSquare, Bot, Zap, Send, Brain, Search, Clock, MessageCircle, ExternalLink, AlignCenter, SquareArrowOutUpRight, Newspaper } from "lucide-react";
import NavigationBar from "../components/NavigationBar";
import Footer from "../components/Footer";
import { Article, getDaysFromDate } from "../components/Articles";
import { useLanguage } from "../contexts/LanguageContext";

import NewsList from "../components/NewsList";

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
            <span className="text-sm font-medium">{t("askhub.hero.pill")}</span>
          </div>
          <h1 className="text-4xl md:text-6xl font-bold text-foreground mb-6">
            {t("nav.ai-chatbot")}
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            {t("askhub.hero.subtitle")}
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
                  placeholder={t("askhub.search.placeholder")}
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
                    {t("askhub.search.button.searching")}
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    {t("askhub.search.button.default")}
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

const SearchResults = ({ query, summary, articles, isLoading, error }: { query: string; summary: string, articles: Article[]; isLoading: boolean; error: string | null }) => {
  const { t } = useLanguage();


  if (error) {
    return (
      <section className="py-16 bg-red-50/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 text-red-600 rounded-full mb-6">
            <Clock className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-red-900 mb-4">
            {t("askhub.error.rate_limit_title") || "Something went wrong"}
          </h2>
          <p className="text-red-700 text-lg max-w-2xl mx-auto">
            {error}
          </p>
        </div>
      </section>
    );
  }

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
              {t("askhub.results.searching_for")} "{query}"...
            </h2>
            <p className="text-muted-foreground text-lg">
              {t("askhub.results.analyzing")}
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
  const [selectedSources, setSelectedSources] = useState<string[]>([]);

  const handleImageError = (id: number) => {
    setImageErrors(prev => ({ ...prev, [id]: true }));
  };

  const toggleSource = (id: string) => {
    setSelectedSources(prev =>
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]
    );
  };

  if (articles.length === 0) return null;

  return (
    <section className="py-16 bg-muted/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-foreground px-4 py-2 mb-4">
            {t("askhub.results.title")} "{query}"
          </h2>

          {/* Summary */}
          <div className="inline-flex items-center gap-2 bg-[#f7c873]/20 text-[#1a2238] px-4 py-2 rounded-full">
            <AlignCenter className="w-4 h-4" />
            <span className="text-md font-medium">{t("askhub.results.summary")}</span>
          </div>
        </div>
        <p className="text-muted-foreground text-lg px-4 py-2">
          {summary}
        </p>

        <NewsList
          articles={articles}
          selectedSources={[]}
          selectedTopics={[]}
        />
      </div>
    </section>
  );
};

const HowItWorksSection = () => {
  const { t } = useLanguage();

  const steps = [
    {
      icon: MessageSquare,
      title: t("askhub.how.step1.title"),
      description: t("askhub.how.step1.desc")
    },
    {
      icon: Brain,
      title: t("askhub.how.step2.title"),
      description: t("askhub.how.step2.desc")
    },
    {
      icon: Zap,
      title: t("askhub.how.step3.title"),
      description: t("askhub.how.step3.desc")
    }
  ];

  return (
    <section className="py-16 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-foreground mb-4">
            {t("askhub.how.title")}
          </h2>
          <p className="text-muted-foreground text-lg">
            {t("askhub.how.subtitle")}
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


export default function AskHubPage() {
  const { t } = useLanguage();
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [articles, setArticles] = useState<Article[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [summary, setSummary] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    setArticles([]);
    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch(`/api/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: query }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        // Handle specific error cases
        if (response.status === 429 && errorData.code === 'RATE_LIMIT') {
          throw new Error(t("askhub.error.rate_limit_msg", { max: errorData.max || 5 }));
        } else if (response.status === 429) {
          throw new Error(errorData.message || "Rate limit exceeded");
        }

        throw new Error(errorData.message || errorData.details || errorData.error || 'Unknown error occurred');
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
        url: item.metadata.url,
        title_es: item.metadata.title_es,
        title_ca: item.metadata.title_ca,
        excerpt_es: item.metadata.excerpt_es,
        excerpt_ca: item.metadata.excerpt_ca,
      }));

      setArticles(transformedArticles || []);
      setSummary(data.summary || "No summary available for this query.");

    } catch (error: any) {
      console.error("Error fetching search results:", error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <NavigationBar activePage="askhub" />
      <HeroSection onSearch={handleSearch} />
      <SearchResults query={searchQuery} summary={summary} articles={articles} isLoading={isLoading} error={error} />
      <HowItWorksSection />
      <Footer />
    </div>
  );
} 