"use client";

import { API_URL, DEFAULT_HEADERS } from "../config";
import { useState, useEffect } from "react";
import { Star } from "lucide-react";


import { useLanguage } from "../contexts/LanguageContext";
import NavigationBar from "../components/NavigationBar";
import Footer from "../components/Footer";
import { Article } from "../components/Articles";
import NewsList from "../components/NewsList";
import { AVAILABLE_SOURCES } from "../components/Mappers";
import NewsFilter from "../components/NewsFilter";


const formatDate = (date: Date): string => date.toISOString().split('T')[0];

interface Topic {
  name: string;
}

const NewsHeader = () => {
  const { t } = useLanguage();
  return (
    <section className="bg-gradient-to-br from-primary/10 to-secondary/10 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 bg-[#f7c873]/20 text-[#1a2238] px-4 py-2 rounded-full mb-6">
            <Star className="w-4 h-4" />
            <span className="text-sm font-medium">{t("latest_news.hero.tagline")}</span>
          </div>
          <h1 className="text-4xl md:text-6xl font-bold text-foreground mb-6">
            {t("nav.latest-news")}
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            {t("latest_news.hero.subtitle")}
          </p>
        </div>
      </div>
    </section>
  );
};


export default function LatestNewsPage() {
  const { t } = useLanguage();
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [availableTopics, setAvailableTopics] = useState<Topic[]>([]);

  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);

  const toggleSource = (id: string) => {
    setSelectedSources(prev =>
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]
    );
  };

  const toggleTopic = (name: string) => {
    setSelectedTopics(prev =>
      prev.includes(name) ? prev.filter(t => t !== name) : [...prev, name]
    );
  };

  const retrieve_news = async () => {
    setLoading(true);
    const today = new Date();
    const pastDate = new Date();
    pastDate.setDate(today.getDate() - 1);

    const allSourceIds = AVAILABLE_SOURCES.map(s => s.id).join(',');

    const payload = {
      limit: 300,
      sources: allSourceIds,
      date_range: {
        from_date: formatDate(pastDate),
        to_date: formatDate(today)
      },
    };
    console.log("Fetching news with payload:", payload);
    try {
      const news_response = await fetch(`${API_URL}/articles`, {
        method: "POST",
        headers: DEFAULT_HEADERS,
        body: JSON.stringify(payload)
      });

      if (!news_response.ok) throw new Error(`HTTP error! Status: ${news_response.status}`);
      const news_data = await news_response.json();

      const topics_response = await fetch(
        `${API_URL}/topics/?from_date=${formatDate(pastDate)}&to_date=${formatDate(today)}`,
        {
          method: "GET",
          headers: DEFAULT_HEADERS,
        }
      );
      if (!topics_response.ok) throw new Error(`HTTP error! Status: ${topics_response.status}`);
      const topics_data = await topics_response.json();
      console.log("Fetched topics data:", topics_data);

      const transformedTopics: Topic[] = topics_data.topics?.map((t: any) => ({
        name: t.name
          .split(' ')
          .map((word: string) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
          .join(' ')
      })) || [];
      setAvailableTopics(transformedTopics);

      const transformedArticles = news_data.articles.map((item: any) => ({
        id: item.id,
        title: item.metadata.title,
        excerpt: item.metadata.excerpt,
        topic: item.metadata.topic
          ? item.metadata.topic
            .split(' ')
            .map((word: string) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ')
          : "Uncategorized",
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

    } catch (error) {
      console.error("Error fetching news:", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    retrieve_news();
  }, []);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <NavigationBar activePage="latest-news" />

      <main className="flex-grow">
        <NewsHeader />
        <NewsFilter
          title={t("latest_news.filters.title")}
          availableSources={AVAILABLE_SOURCES}
          selectedSources={selectedSources}
          toggleSource={toggleSource}
          availableTopics={availableTopics}
          selectedTopics={selectedTopics}
          toggleTopic={toggleTopic}
        />

        {loading ? (
          <div className="flex justify-center items-center py-32">
            <div className="flex flex-col items-center">
              <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
              <p className="text-muted-foreground animate-pulse">{t("latest_news.loading")}</p>
            </div>
          </div>
        ) : (
          <NewsList
            articles={articles}
            selectedSources={selectedSources}
            selectedTopics={selectedTopics}
          />
        )}
      </main>

      <Footer />
    </div>
  );
}