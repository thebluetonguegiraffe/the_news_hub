import { useMemo, useState } from "react";
import { Calendar, ExternalLink, Newspaper } from "lucide-react";
import { Article, getDaysFromDate } from "./Articles";
import RobustImageComponent from "./RobustImage";
import { AVAILABLE_SOURCES } from "./Mappers";
import { useLanguage } from "../contexts/LanguageContext";

const getSourceIcon = (sourceUrl: string) => {
  const s = sourceUrl?.toLowerCase() || "";
  const match = AVAILABLE_SOURCES.find(src => s.includes(src.id.toLowerCase()));
  return match ? match.icon : null;
};

const getSourceName = (url: string) => {
  const s = url?.toLowerCase() || "";
  const match = AVAILABLE_SOURCES.find(src => s.includes(src.id.toLowerCase()));
  return match ? match.name : "news_list.source_default";
};

interface NewsListProps {
  articles: Article[];
  selectedSources?: string[];
  selectedTopics?: string[];
}

const NewsList: React.FC<NewsListProps> = ({
  articles,
  selectedSources = [],
  selectedTopics = []
}) => {
  const { t } = useLanguage();

  const filteredArticles = useMemo(() => {
    if (selectedSources.length === 0 && selectedTopics.length === 0) {
      return articles;
    }

    return articles.filter(article => {
      const sourceUrl = article.source.toLowerCase();

      const matchesSource = selectedSources.length === 0 ||
        selectedSources.some(id => sourceUrl.includes(id.toLowerCase()));

      const matchesTopic = selectedTopics.length === 0 ||
        selectedTopics.includes(article.topic);

      return matchesSource && matchesTopic;
    });
  }, [articles, selectedSources, selectedTopics]);

  return (
    <section className="py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        {filteredArticles.length === 0 ? (
          <div className="text-center py-20 bg-gray-50 rounded-lg border border-dashed border-gray-300">
            <p className="text-muted-foreground text-lg">{t("news_list.no_articles")}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredArticles.map((article) => (
              <div key={article.id} className="bg-card border border-r rounded-lg overflow-hidden hover:shadow-lg transition-all duration-300 group">
                <div className="aspect-video bg-muted relative overflow-hidden">
                  <RobustImageComponent
                    images={article.image}
                    alt={article.title}
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                    fallback={
                      <div className="w-full h-full bg-gradient-to-br from-[#f7c873]/20 to-[#f7c873]/10 flex items-center justify-center">
                        <Newspaper className="w-12 h-12 text-[#f7c873]" />
                      </div>
                    }
                  />

                  {/* Source icon*/}
                  {getSourceIcon(article.source) && (
                    <div className="absolute top-3 right-3 w-10 h-10 bg-white rounded-full p-1.5 shadow-md border border-gray-100 flex items-center justify-center z-10">
                      <img
                        src={getSourceIcon(article.source)!}
                        alt={article.source}
                        className="w-full h-full object-contain rounded-full"
                      />
                    </div>
                  )}

                  {/* Topic Badge */}
                  <div className="absolute top-3 left-3">
                    <span className="px-3 py-1 bg-[#f7c873] text-[#1a2238] text-xs font-bold rounded-full shadow-sm">
                      {article.topic}
                    </span>
                  </div>
                </div>

                <div className="p-6 flex flex-col h-auto min-h-[200px]">
                  <div className="flex items-center text-xs text-muted-foreground mb-3">
                    <Calendar className="w-3.5 h-3.5 mr-1.5" />
                    {getDaysFromDate(article.date, t)}
                    <span className="mx-2 text-gray-300">•</span>
                    <span className="font-semibold uppercase tracking-wider text-primary/80">
                      {getSourceName(article.source) === "news_list.source_default"
                        ? t(getSourceName(article.source))
                        : getSourceName(article.source)}
                    </span>
                  </div>

                  <h3 className="text-xl font-bold text-foreground mb-3 line-clamp-2 leading-tight group-hover:text-primary transition-colors">
                    {article.title}
                  </h3>

                  <p className="text-muted-foreground text-sm mb-4 line-clamp-3 flex-grow">
                    {article.excerpt}
                  </p>

                  <div className="mt-auto pt-4 border-t border-gray-100">
                    <a
                      href={article.url}
                      className="inline-flex items-center gap-1.5 text-sm font-semibold text-primary hover:text-primary/80 transition-colors"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {t("news_list.read_more")}
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
};

export default NewsList;