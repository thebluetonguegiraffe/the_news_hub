"use client";

import { API_URL, DEFAULT_HEADERS } from "../../config";
import { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { useParams, useSearchParams } from 'next/navigation';

import NavigationBar from "../../components/NavigationBar";
import Footer from "../../components/Footer";
import NewsList from "../../components/NewsList";
import { Article } from "../../components/Articles";
import iconMap, { AVAILABLE_SOURCES } from "@/app/components/Mappers";
import NewsFilter from "@/app/components/NewsFilter";
import { useLanguage } from "@/app/contexts/LanguageContext";

const formatDate = (date: Date): string => date.toISOString().split('T')[0];

interface TopicHeaderProps {
  title: string;
  description?: string;
  category?: string;
}

const TopicHeader = ({ title, description, category }: TopicHeaderProps) => {
  const IconComponent = iconMap[title] || iconMap[category || ""] || iconMap["Default"];

  return (
    <section className="bg-gradient-to-br from-primary/10 to-secondary/10 py-12 md:py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center flex flex-col items-center">
          <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-[#f7c873]/20 text-[#1a2238] shadow-md mb-6">
            {IconComponent && <IconComponent className="w-6 h-6" />}
          </div>
          <h1 className="text-4xl md:text-6xl font-bold text-slate-900 dark:text-white mb-6 capitalize">
            {title}
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            {description || ""}
          </p>
        </div>
      </div>
    </section>
  );
};

export default function ArticlePage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [topicDescription, setTopicDescription] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const params = useParams();
  const searchParams = useSearchParams();

  const topicName = decodeURIComponent(params.topicName as string);
  const fromDate = searchParams.get('from');
  const toDate = searchParams.get('to');

  const retrieve_description = async () => {
    if (!topicName) return;
    try {
      const response = await fetch(`${API_URL}/topics/description/${encodeURIComponent(topicName)}`, {
        method: "GET",
        headers: DEFAULT_HEADERS,
      });

      if (response.ok) {
        const data = await response.json();
        setTopicDescription(data.description || data);
      }
    } catch (error) {
      console.error("Error fetching topic description:", error);
    }
  };

  const retrieve_news = async () => {
    if (!topicName) return;
    setLoading(true);
    try {
      const requestBody = {
        topic: topicName,
        date_range: {
          from_date: fromDate ? formatDate(new Date(fromDate)) : null,
          to_date: toDate ? formatDate(new Date(toDate)) : null
        },
        limit: 100
      };

      const response = await fetch(`${API_URL}/articles`, {
        method: "POST",
        headers: DEFAULT_HEADERS,
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) throw new Error(`Status: ${response.status}`);

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
    } catch (error) {
      console.error("Error fetching search results:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    retrieve_news();
    retrieve_description();
  }, [topicName, fromDate, toDate]);

  const [selectedSources, setSelectedSources] = useState<string[]>([]);

  const toggleSource = (id: string) => {
    setSelectedSources(prev =>
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]
    );
  };

  return (
    <div className="min-h-screen bg-background">
      <NavigationBar activePage="menu" />
      <TopicHeader
        title={topicName}
        description={topicDescription}
      />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-12">
        <div className="mb-8">
          <NewsFilter
            title="Filters"
            availableSources={AVAILABLE_SOURCES}
            selectedSources={selectedSources}
            toggleSource={toggleSource}
          />
        </div>
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
              <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            </div>
          </div>
        ) : (
          <NewsList
            articles={articles}
            selectedSources={selectedSources}
            selectedTopics={[]}
          />
        )}
        <div className="mt-16 mb-8 flex justify-center">
          <Link
            href="/hot-topics"
            className="inline-flex items-center gap-2 bg-card border px-6 py-3 text-muted-foreground rounded-full hover:bg-[#f7c873]/20 hover:text-foreground hover:border-[#f7c873]/50 transition-all duration-300 shadow-sm group"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform duration-200" />
            <span className="font-medium">Go back to Hot Topics</span>
          </Link>
        </div>
      </main>
      <Footer />
    </div>
  );
}