"use client";

import { API_URL, DEFAULT_HEADERS } from "../config";

import { useState, useEffect } from "react";
import {
  Calendar,
  ExternalLink,
  Newspaper,
  Star
} from "lucide-react";
import { useLanguage } from "../contexts/LanguageContext";


import NavigationBar from "../components/NavigationBar";
import Footer from "../components/Footer";
import { Article, getDaysFromDate } from "../components/Articles";
import RobustImageComponent from "../components/RobustImage";


const NewsHeader = () => {
  const { t } = useLanguage();

  return (
    <section className="bg-gradient-to-br from-primary/10 to-secondary/10 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 bg-[#f7c873]/20 text-[#1a2238] px-4 py-2 rounded-full mb-6">
            <Star className="w-4 h-4" />
            <span className="text-sm font-medium">AI-Powered News</span>
          </div>
          <h1 className="text-4xl md:text-6xl font-bold text-foreground mb-6">
            {t("nav.latest-news")}
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            Stay informed with the latest news, breaking stories, and in-depth analysis from around the world.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          </div>
        </div>
      </div>
    </section>
  );
};

type NewsListProps = {
  articles: Article[];
};


const NewsList: React.FC<NewsListProps> = ({ articles }) => {
  const { t } = useLanguage();
  const [imageErrors, setImageErrors] = useState<{ [key: number]: boolean }>({});

  const handleImageError = (id: number) => {
    setImageErrors(prev => ({ ...prev, [id]: true }));
  };

  return (
    <section className="py-16 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Recent News */}
        <div>
          <h2 className="text-2xl font-bold text-foreground mb-6">Recent News</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {articles.map((article) => (
              <div key={article.id} className="bg-card border border-border rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
                <div className="aspect-video bg-muted relative">
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
                  <div className="absolute top-2 left-2">
                    <span className="px-3 py-1 bg-[#f7c873] text-[#1a2238] text-xs font-semibold rounded-full">
                      {article.topic}
                    </span>
                  </div>
                </div>
                <div className="p-6">
                  <div className="flex items-center text-sm text-muted-foreground mb-2">
                    <Calendar className="w-4 h-4 mr-1" />
                    {getDaysFromDate(article.date)}
                  </div>
                  <h3 className="text-lg font-semibold text-foreground mb-2 line-clamp-2">
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
      </div>
    </section>
  );
};

const SourcesSection = () => {

  const sources = [
    {
      name: "The Washington Post",
      abbreviation: "TWP",
      description: "Leading American daily newspaper",
      logo: "/images/WP.png"
    },
    {
      name: "The New York Times",
      abbreviation: "TNYT",
      description: "International daily newspaper",
      logo: "/images/nyt.png"
    },
    {
      name: "BBC News",
      abbreviation: "BBC",
      description: "British public service broadcaster",
      logo: "/images/BBC.jpg"
    },
    { 
      name: "The Guardian News",
      abbreviation: "The Guardian",
      description: "Global Independent journalism voicer",
      logo: "/images/the_guardian.jpg"
    }
  ];


  return (
    <section className="py-16 bg-muted/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-[#f7c873]/20 rounded-full mb-6">
            <Newspaper className="w-8 h-8 text-[#f7c873]" />
          </div>
          <h2 className="text-3xl font-bold text-foreground mb-4">
            Our Trusted News Sources
          </h2>
          <p className="text-muted-foreground text-lg">
            We partner with the world's most reputable news organizations to bring you accurate, timely, and comprehensive coverage.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {sources.map((source) => (
            <div 
              key={source.abbreviation} 
              className="bg-card flex flex-col items-center text-center p-6 border border-border rounded-lg shadow hover:shadow-md transition-shadow group"
            >
              <div className="w-20 h-20 overflow-hidden rounded-full bg-white flex items-center justify-center mb-4">
                <img 
                  src={source.logo} 
                  alt={source.name} 
                  className="w-full h-full object-contain p-2" 
                />
              </div>
              <h3 className="text-lg font-semibold">{source.name}</h3>
              <p className="text-md text-muted-foreground">{source.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default function LatestNewsPage() {

  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);

  const retrieve_news = async () => {
    setLoading(true);
    try {
      console.log("Request:", {
        url: `${API_URL}/latest_news`,
        method: "GET",
        headers: DEFAULT_HEADERS,
        credentials: "include",
      });

      const response = await fetch(`${API_URL}/latest_news`, {
        method: "GET",
        headers: DEFAULT_HEADERS,
        credentials: 'include',
      });
      console.log(response)

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      setArticles(data.articles || []);

    } catch (error) {
      console.error("Error fetching search results:", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    retrieve_news();
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* TODO */}
      <NavigationBar activePage="noticias" />
      <NewsHeader />

      {loading ? (
        <div className="flex justify-center items-center min-h-screen">
          <div className="mt-20">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-full mb-6">
              <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            </div>
          </div>
        </div>
      ) : (
        <NewsList articles={articles} />
      )}

      <SourcesSection />
      <Footer />
    </div>
  );
} 
