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

const capitalize = (str: string | undefined | null) => {
  if (!str) return "";
  return str
    .split(' ')
    .map((word: string) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

interface TopicHeaderProps {
  title: string;
  description?: string;
  category?: string;
}

const TopicHeader = ({ title, description, category }: TopicHeaderProps) => {
  const normalize = (str: string) => str.toLowerCase().trim();
  const iconKey = Object.keys(iconMap).find(k =>
    normalize(k) === normalize(category || "") ||
    normalize(k) === normalize(title)
  );
  const IconComponent = iconKey ? iconMap[iconKey] : iconMap["Default"] || iconMap["politics"]; // Fallback to something valid if Default missing

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
  const { t, language } = useLanguage();
  const [articles, setArticles] = useState<Article[]>([]);
  const [topicData, setTopicData] = useState<{
    description: string;
    topic_es?: string;
    topic_ca?: string;
    description_es?: string;
    description_ca?: string;
  } | null>(null);
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
        setTopicData(data);
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
        url: item.metadata.url,
        title_es: item.metadata.title_es,
        title_ca: item.metadata.title_ca,
        excerpt_es: item.metadata.excerpt_es,
        excerpt_ca: item.metadata.excerpt_ca,
        topic_es: item.metadata.topic_es,
        topic_ca: item.metadata.topic_ca,
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
        title={
          capitalize(
            language === "es"
              ? topicData?.topic_es || topicName
              : language === "ca"
                ? topicData?.topic_ca || topicName
                : topicName
          )
        }
        category={capitalize(topicName)}
        description={
          capitalize(
            language === "es"
              ? topicData?.description_es || topicData?.description
              : language === "ca"
                ? topicData?.description_ca || topicData?.description
                : topicData?.description
          )
        }
      />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-12">
        <div className="mb-8">
          <NewsFilter
            title={t("topic_page.filters")}
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
            className="inline-flex items-center gap-2 bg-[#f7c873] border border-[#f7c873] px-6 py-3 text-[#1a2238] rounded-full hover:bg-[#f7c873]/90 hover:text-[#1a2238] transition-all duration-300 shadow-sm group"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform duration-200" />
            <span className="font-medium">{t("topic_page.back")}</span>
          </Link>
        </div>
      </main>
      <Footer />
    </div>
  );
}