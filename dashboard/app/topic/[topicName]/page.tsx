"use client";

import { useState, useEffect } from "react";

import Link from "next/link";

import { ArrowLeft, Calendar, ExternalLink, Newspaper} from "lucide-react";

import { useParams } from "next/navigation";
import { useSearchParams } from 'next/navigation';

import { useLanguage } from "../../contexts/LanguageContext";

import NavigationBar from "../../components/NavigationBar";
import Footer from "../../components/Footer";
import { Article, getDaysFromDate } from "../../components/Articles";
import RobustImageComponent from "../../components/RobustImage";


type NewsListProps = {
  articles: Article[];
};

const NewsByTopicList: React.FC<NewsListProps> = ({ articles }) => {
  const { t } = useLanguage();

  return (
    <section className="py-16 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <Link
            href="/hot-topics"
            className="inline-flex items-center text-primary hover:text-primary/80 transition-colors"
          >
            <div className="inline-flex items-center gap-2 bg-[#f7c873]/20 text-[#1a2238] px-4 py-2 rounded-full mb-6">
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm font-medium"> Go back to Hot Topics</span>
            </div>
          </Link>
        </div>
        {/* Recent News */}
        <div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {articles.map((article) => (
              <div key={article.id} className="bg-card border border-border rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
                <div className="aspect-video bg-muted relative">
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
                  <div className="absolute top-2 left-2">
                    <span className="px-3 py-1 bg-[#f7c873] text-[#1a2238] text-xs font-semibold rounded-full">
                      {article.topic}
                    </span>
                  </div>
                </div>
                <div className="p-6">
                  <div className="flex items-center text-sm text-muted-foreground mb-2">
                    <Calendar className="w-4 h-4 mr-1" />
                    {new Date(article.date).toISOString().split("T")[0]}
                    { ` | ` }
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

export default function ArticlePage() {
    const [articles, setArticles] = useState<Article[]>([]);
    const [loading, setLoading] = useState(false);
   
    const params = useParams();
    const searchParams = useSearchParams();
    
    const topicName = params.topicName;
    const fromDate = searchParams.get('from')
    const toDate = searchParams.get('to')
    
    const retrieve_news = async () => {
      if (!topicName) return;
        setLoading(true);
        try {
          const response = await fetch(`http://localhost:7000/articles/${topicName}?from=${fromDate}&to=${toDate}`, {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            },
          });
   
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
    }, [topicName, fromDate, toDate]) // Add fromDate and toDate as dependencies
   
  return (
    <div className="min-h-screen bg-background">
      <NavigationBar activePage="inicio" />
      {loading ? (
        <div className="flex justify-center items-center min-h-screen">
          <div className="mt-20">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-full mb-6">
              <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            </div>
          </div>
        </div>
      ) : (
        <NewsByTopicList articles={articles} />
      )}
      <Footer />
    </div>
  );
}