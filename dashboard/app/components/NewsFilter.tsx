import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Hash } from 'lucide-react';
import iconMap from './Mappers';
import { useLanguage } from '../contexts/LanguageContext';

const defaultGetTopicIcon = (topicName: string): React.ElementType => {
  const normalize = (str: string) => str.toLowerCase().trim();
  const key = Object.keys(iconMap).find(k => normalize(k) === normalize(topicName));
  return key ? iconMap[key] : Hash;
};

interface NewsFilterProps {
  title?: string;
  selectedSources?: string[];
  toggleSource?: (id: string) => void;
  availableSources?: { id: string; name: string; icon: string }[];
  availableTopics?: { name: string }[];
  selectedTopics?: string[];
  toggleTopic?: (name: string) => void;
  getTopicIcon?: (name: string) => React.ElementType;
}

const NewsFilter = ({
  title = "Filters",
  selectedSources,
  toggleSource,
  availableSources = [],
  availableTopics,
  selectedTopics,
  toggleTopic,
  getTopicIcon = defaultGetTopicIcon
}: NewsFilterProps) => {
  const { t } = useLanguage();
  const [isSourcesOpen, setIsSourcesOpen] = useState(false);
  const [isTopicsOpen, setIsTopicsOpen] = useState(false);

  const sourcesRef = useRef<HTMLDivElement>(null);
  const topicsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (sourcesRef.current && !sourcesRef.current.contains(event.target as Node)) setIsSourcesOpen(false);
      if (topicsRef.current && !topicsRef.current.contains(event.target as Node)) setIsTopicsOpen(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const showSources = selectedSources !== undefined && toggleSource !== undefined;
  const showTopics = availableTopics !== undefined && selectedTopics !== undefined && toggleTopic !== undefined;

  return (
    <div className="w-full bg-gray-50/80 sticky top-0 z-20 backdrop-blur-md pt-6 pb-4">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between border-b border-gray-300 pb-8">
          <h1 className="text-3xl font-bold mt-8 text-gray-800">{title}</h1>

          <div className="flex items-center gap-3">

            {showSources && (
              <div className="relative" ref={sourcesRef}>
                <button
                  onClick={() => setIsSourcesOpen(!isSourcesOpen)}
                  className={`flex items-center gap-2 px-5 py-2 rounded-full transition-all duration-200 text-[#1a2238] font-medium text-sm border ${isSourcesOpen ? 'bg-[#f7c873]/40 border-[#f7c873]/50' : 'bg-[#f7c873]/20 border-transparent hover:bg-[#f7c873]/30'
                    }`}
                >
                  <span><b>{t("news_filter.sources")}</b></span>
                  <ChevronDown className={`w-3.5 h-3.5 ml-1 transition-transform ${isSourcesOpen ? 'rotate-180' : ''}`} />
                </button>

                {isSourcesOpen && (
                  <div className="absolute top-full right-0 mt-3 w-72 bg-white rounded-xl shadow-xl border border-blue-100 overflow-hidden z-50 animate-in fade-in zoom-in-95 duration-100">
                    <div className="p-3 max-h-[300px] overflow-y-auto custom-scrollbar space-y-1">
                      {availableSources.map((source) => {
                        const isSelected = selectedSources.includes(source.id);
                        return (
                          <div
                            key={source.id}
                            onClick={() => toggleSource(source.id)}
                            className={`flex items-center gap-3 p-2.5 rounded-lg cursor-pointer transition-all border ${isSelected ? 'bg-blue-50 border-blue-200 text-blue-900 shadow-sm' : 'bg-transparent border-transparent hover:bg-gray-50 text-gray-700'
                              }`}
                          >
                            <div className="w-9 h-9 bg-white rounded-md flex items-center justify-center border border-gray-100 shadow-sm overflow-hidden shrink-0">
                              <img src={source.icon} alt={source.name} className="w-7 h-7 object-contain" />
                            </div>
                            <span className={`text-sm ${isSelected ? 'font-semibold' : 'font-medium'}`}>{source.name}</span>
                          </div>
                        );
                      })}
                    </div>
                    <div className="bg-gray-50 p-3 border-t flex justify-between">
                      <button onClick={() => availableSources.forEach(s => !selectedSources.includes(s.id) && toggleSource(s.id))} className="text-xs font-semibold hover:underline">{t("news_filter.select_all")}</button>
                      <button onClick={() => selectedSources.forEach(id => toggleSource(id))} className="text-xs font-semibold text-red-500">{t("news_filter.clear")}</button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {showTopics && (
              <div className="relative" ref={topicsRef}>
                <button
                  onClick={() => setIsTopicsOpen(!isTopicsOpen)}
                  className={`flex items-center gap-2 px-5 py-2 rounded-full transition-all duration-200 text-[#1a2238] font-medium text-sm border ${isTopicsOpen ? 'bg-[#f7c873]/40 border-[#f7c873]/50' : 'bg-[#f7c873]/20 border-transparent hover:bg-[#f7c873]/30'
                    }`}
                >
                  <span><b>{t("news_filter.topics")}</b></span>
                  <ChevronDown className={`w-3.5 h-3.5 ml-1 transition-transform ${isTopicsOpen ? 'rotate-180' : ''}`} />
                </button>

                {isTopicsOpen && (
                  <div className="absolute top-full right-0 mt-3 w-72 bg-white rounded-xl shadow-xl border border-blue-100 overflow-hidden z-50 animate-in fade-in zoom-in-95 duration-100">
                    <div className="p-3 max-h-[300px] overflow-y-auto custom-scrollbar space-y-1">
                      {availableTopics.map((topic) => {
                        const isSelected = selectedTopics.includes(topic.name);
                        const TopicIcon = getTopicIcon(topic.name);
                        return (
                          <div
                            key={topic.name}
                            onClick={() => toggleTopic(topic.name)}
                            className={`flex items-center gap-3 p-2.5 rounded-lg cursor-pointer transition-all border ${isSelected ? 'bg-blue-50 border-blue-200 text-blue-900 shadow-sm' : 'bg-transparent border-transparent hover:bg-gray-50 text-gray-700'
                              }`}
                          >
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isSelected ? 'bg-blue-200 text-blue-700' : 'bg-gray-100 text-gray-400'}`}>
                              <TopicIcon className="w-4 h-4" />
                            </div>
                            <span className={`text-sm ${isSelected ? 'font-semibold' : 'font-medium'}`}>{topic.name}</span>
                          </div>
                        );
                      })}
                    </div>
                    <div className="bg-gray-50 p-3 border-t flex justify-between">
                      <button onClick={() => availableTopics.forEach(t => !selectedTopics.includes(t.name) && toggleTopic(t.name))} className="text-xs font-semibold hover:underline">{t("news_filter.select_all")}</button>
                      <button onClick={() => selectedTopics.forEach(id => toggleTopic(id))} className="text-xs font-semibold text-red-500">{t("news_filter.clear")}</button>
                    </div>
                  </div>
                )}
              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  );
};

export default NewsFilter;