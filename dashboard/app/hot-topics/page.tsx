"use client";

import { API_URL, DEFAULT_HEADERS } from "../config";


import { useState, useEffect } from "react";
import { TrendingUp, Users, BarChart3, ArrowRight, ShieldCheck, Star, Zap, AlertTriangle, Globe, Building2, Trophy, Film, Microscope, ExternalLink, BookOpen, Music, Globe2, Leaf, Heart, BarChart2 } from "lucide-react";
import NavigationBar from "../components/NavigationBar";
import Footer from "../components/Footer";
import CalendarComponent from "../components/Calendar";
import { useLanguage } from "../contexts/LanguageContext";

const HeaderSection = () => {
  const { t } = useLanguage();

  return (
    <section className="bg-gradient-to-br from-primary/10 to-secondary/10 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 bg-[#f7c873]/20 text-[#1a2238] px-4 py-2 rounded-full mb-6">
            <TrendingUp className="w-4 h-4" />
            <span className="text-sm font-medium">Trending Now</span>
          </div>
          <h1 className="text-4xl md:text-6xl font-bold text-foreground mb-6">
            {t("nav.hot-topics")}
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            Discover the most trending topics and breaking stories that are shaping our world today.
          </p>
        </div>
      </div>
    </section>
  );
};

type Topic = {
  name: string;
  topics_per_day: Record<string, number>;
  count: number;
  description: string;
  icon?: React.ComponentType<React.SVGProps<SVGSVGElement>> | null;
};


const defaultIcon = TrendingUp;


const iconMap: Record<string, React.ComponentType<any>> = {
  politics: Globe,               // political globe icon
  government: ShieldCheck,       // official, safety or authority icon
  economy: BarChart2,            // market/economic data
  business: Building2,           // company/building icon
  science: Microscope,           // research/science
  technology: Zap,               // lightning bolt = innovation/tech
  health: Heart,                 // medical/health icon
  environment: Leaf,             // nature/environment
  "world News": Globe2,          // global news, world map icon
  sports: Trophy,                // sports trophies
  arts: Music,                  // music note for arts (visual/music)
  culture: BookOpen,             // books, knowledge, culture
  crime: AlertTriangle,          // warning icon for crime
  "public Safety": Users,        // community safety (people/users)
};

function toLocalMidnightISOString(date: Date) {
  const localMidnightUTC = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return localMidnightUTC.toISOString().split("T")[0];
}

const HotTopicsSection = () => {
  const { t } = useLanguage();
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const [selectedDateRange, setSelectedDateRange] = useState<{
  fromDate: Date;
  toDate: Date;
  } | null>({
    fromDate: yesterday,
    toDate: yesterday,
  });

  const [topics, setTopics] = useState<Topic[]>([]);
  const [fromDate, setFromDate] = useState<string | null>(null);
  const [toDate, setToDate] = useState<string | null>(null);


  const handleDateSelect = (date: Date) => {
    setSelectedDate(date);
  };

  
  const handleDateRangeSelect = (fromDate: Date, toDate: Date) => {
    setSelectedDateRange({ fromDate, toDate });
  };
  

  useEffect(() => {
    const fetchTopics = async () => {
      if (!selectedDateRange?.fromDate || !selectedDateRange?.toDate) return;

      const fromDate = toLocalMidnightISOString(selectedDateRange.fromDate);
      const toDate = toLocalMidnightISOString(selectedDateRange.toDate);

      setFromDate(fromDate);
      setToDate(toDate);

      try {
        const response = await fetch(
          `${API_URL}/topics?from_date=${fromDate}&to_date=${toDate}`,
          {
            method: "GET",
            headers: DEFAULT_HEADERS,
          }
        );
        const data = await response.json();

        // Ensure data is an array and handle different response structures
        const topicsArray = Array.isArray(data) ? data : data.topics || data.data || [];

        const topicsWithIcons = topicsArray.map((topic: Omit<Topic, "icon" | "count">) => {
            // sum up all counts in topics_per_day
            const count = Object.values(topic.topics_per_day || {}).reduce(
              (sum, val) => sum + (typeof val === "number" ? val : 0),
              0
            );

            return {
              ...topic,
              count, // now each topic has a count
              icon: iconMap[topic.name] ?? defaultIcon,
            };
        });
        setTopics(topicsWithIcons); // make sure the API returns an array of { name, count, icon, description }
      } catch (error) {
        console.error("Failed to fetch topics:", error);
      }
    };

    fetchTopics();
  }, [selectedDateRange]);



  return (
    <section className="py-16 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left side - Calendar */}
          <div className="lg:col-span-1">
            <div className="sticky top-24">
              <CalendarComponent
                onDateSelect={handleDateSelect}
                onDateRangeSelect={handleDateRangeSelect}
                selectedDate={selectedDate}
                selectedDateRange={selectedDateRange}
              />
            </div>
          </div>

          {/* Right side - Trending Topics */}
          <div className="lg:col-span-2">
            {topics.length === 0 ? (
              <div className="bg-card border border-border rounded-lg p-6 flex flex-col items-center justify-center min-h-[400px] space-y-6">
              <p className="text-xl font-semibold text-foreground  mb-6">
              No topics registered during this range of dates
              </p>
              <p className="text-muted-foreground text-center text-lg opacity-75  mb-6">
                Please select a different range of dates.
              </p>
              <div className="flex flex-wrap justify-center gap-8">
                {Object.entries(iconMap).map(([category, Icon]) => (
                  <div
                    key={category}
                    className="inline-flex items-center justify-center w-12 h-12 bg-[#f7c873]/20 text-[#1a2238] rounded-lg group-hover:bg-[#f7c873] transition-colors"
                  >
                    <Icon className="w-6 h-6" />
                  </div>
                ))}
              </div>
            </div>
            ) : (

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {topics.map((topic, index) => (
                  <div key={index} className="bg-card border border-border rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer group">
                    <div className="flex items-center justify-between mb-4">
                      <div className="inline-flex items-center justify-center w-12 h-12 bg-[#f7c873]/20 text-[#1a2238] rounded-lg group-hover:bg-[#f7c873] transition-colors">
                        {topic.icon && <topic.icon className="w-6 h-6" />}
                      </div>
                      <div className="text-right">
                        <span className="text-sm font-medium text-primary bg-primary/10 px-2 py-1 rounded-full">
                          {topic.count} news
                        </span>
                      </div>
                    </div>
                    <h3 className="text-lg font-semibold text-foreground mb-2 group-hover:text-primary transition-colors">
                      {topic.name.charAt(0).toUpperCase() + topic.name.slice(1)}
                    </h3>
                    <p className="text-muted-foreground mb-4 text-sm">
                      {topic.description}
                    </p>
                    <div className="flex items-center justify-between">
                    <a
                      href={`/topic/${topic.name}?from=${fromDate}&to=${toDate}`}
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
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default function HotTopicsPage() {
  return (
    <div className="min-h-screen bg-background">
      <NavigationBar activePage="tema-caliente" />
      <HeaderSection />
      <HotTopicsSection />
      <Footer />
    </div>
  );
} 