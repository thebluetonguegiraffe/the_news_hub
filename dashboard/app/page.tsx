"use client";

import { useState } from "react";
import { ArrowRight, CheckCircle, MessageCircle, TrendingUp, Users, Zap, Star } from "lucide-react";
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
            <span className="text-sm font-medium">AI-Powered News</span>
          </div>
          <h1 className="text-4xl md:text-6xl font-bold text-foreground mb-6">
            Welcome to <span className="text-[#3a5ba0]">The News Hub</span>
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


const FAQSection = () => {
  const { t } = useLanguage();
  
  const faqs = [
    {
      question: t("faq.ai.question"),
      answer: t("faq.ai.answer")
    },
    {
      question: t("faq.updates.question"),
      answer: t("faq.updates.answer")
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
          <p className="text-muted-foreground text-lg">
            {t("faq.subtitle")}
          </p>
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
      <NavigationBar activePage="inicio" />
      <HeroSection />
      <FeaturesSection />
      <FAQSection />
      <Footer />
    </div>
  );
}
