"use client";

import { ArrowRight, MessageCircle, TrendingUp, Zap, Star, Newspaper } from "lucide-react";
import Link from "next/link";
import NavigationBar from "./components/NavigationBar";
import Footer from "./components/Footer";
import { useLanguage } from "./contexts/LanguageContext";

const HeroSection = () => {
  const { t } = useLanguage();

  return (
    <section className="bg-gradient-to-br from-primary/10 to-secondary/10 py-16 relative overflow-hidden">
      {/* Yellow accent elements */}
      <div className="absolute top-10 left-10 w-20 h-20 bg-[#f7c873]/20 rounded-full blur-xl"></div>
      <div className="absolute bottom-10 right-10 w-32 h-32 bg-[#f7c873]/15 rounded-full blur-xl"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 bg-[#f7c873]/20 text-[#1a2238] px-4 py-2 rounded-full mb-6">
            <Star className="w-4 h-4" />
            <span className="text-sm font-medium">{t("home.hero.tagline")}</span>
          </div>
          <h1 className="text-4xl md:text-6xl font-bold text-foreground mb-6">
            {t("home.hero.welcome")} <span className="text-[#3a5ba0]">{t("home.hero.brand")}</span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            {t("home.hero.subtitle")}
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/latest-news"
              className="inline-flex items-center px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
              {t("home.hero.explore")}
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
            <Link
              href="/askhub"
              className="inline-flex items-center px-6 py-3 border-2 border-[#1a2238] text-[#1a2238] rounded-lg hover:bg-[#1a2238] hover:text-white transition-colors font-semibold"
            >
              {t("home.hero.try-ai")}
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
};

const FeaturesSection = () => {
  const { t } = useLanguage();

  const features = [
    {
      icon: TrendingUp,
      title: t("features.news.title"),
      description: t("features.news.description")
    },
    {
      icon: Zap,
      title: t("features.topics.title"),
      description: t("features.topics.description")
    },
    {
      icon: MessageCircle,
      title: t("features.ai.title"),
      description: t("features.ai.description")
    }
  ];

  return (
    <section className="py-16 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-[#f7c873]/20 rounded-full mb-6">
            <Zap className="w-8 h-8 text-[#f7c873]" />
          </div>
          <h2 className="text-3xl font-bold text-foreground mb-4">
            {t("features.title")}
          </h2>
          <p className="text-muted-foreground text-lg">
            {t("features.subtitle")}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="bg-card border border-border rounded-lg p-6 text-center hover:shadow-md transition-shadow relative group">
              {/* Yellow accent border on hover */}
              <div className="absolute inset-0 rounded-lg border-2 border-[#f7c873] opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative z-10">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-[#f7c873]/20 text-[#f7c873] rounded-lg mb-4 group-hover:bg-[#f7c873] group-hover:text-[#1a2238] transition-colors">
                  <feature.icon className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-2">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};



const SourcesSection = () => {
  const { t } = useLanguage();

  const sources = [
    {
      name: "The Washington Post",
      abbreviation: "TWP",
      description: t("sources.twp.description"),
      logo: "/images/WP.png"
    },
    {
      name: "The New York Times",
      abbreviation: "TNYT",
      description: t("sources.nyt.description"),
      logo: "/images/nyt.png"
    },
    {
      name: "BBC News",
      abbreviation: "BBC",
      description: t("sources.bbc.description"),
      logo: "/images/BBC.jpg"
    },
    {
      name: "The Guardian News",
      abbreviation: "The Guardian",
      description: t("sources.guardian.description"),
      logo: "/images/the_guardian.jpg"
    },
    {
      name: "Ara.cat",
      abbreviation: "Ara",
      description: t("sources.ara.description"),
      logo: "/images/ara.png"
    },
    {
      name: "La Vanguardia",
      abbreviation: "La Vanguardia",
      description: t("sources.lavanguardia.description"),
      logo: "/images/la-vanguardia.png"
    },
    {
      name: "El País",
      abbreviation: "El País",
      description: t("sources.elpais.description"),
      logo: "/images/el-país.png"
    },
    {
      name: "El Periodico",
      abbreviation: "El Periodico",
      description: t("sources.elperiodico.description"),
      logo: "/images/el-periodico.png"
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
            {t("sources.title")}
          </h2>
          <p className="text-muted-foreground text-lg">
            {t("sources.subtitle")}
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

const FAQSection = () => {
  const { t } = useLanguage();

  const faqs = [
    {
      question: t("faq.updates.question"),
      answer: t("faq.updates.answer")
    },
    {
      question: t("faq.ai.question"),
      answer: t("faq.ai.answer")
    },

    {
      question: t("faq.personalize.question"),
      answer: t("faq.personalize.answer")
    },
    {
      question: t("faq.free.question"),
      answer: t("faq.free.answer")
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


export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <NavigationBar activePage="menu" />
      <HeroSection />
      <FeaturesSection />
      <SourcesSection />
      <FAQSection />
      <Footer />
    </div>
  );
}
