"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { useLanguage } from "../contexts/LanguageContext";
import { Globe } from "lucide-react";

interface NavigationBarProps {
  activePage: "inicio" | "noticias" | "tema-caliente" | "ia";
}

const NavigationBar = ({ activePage }: NavigationBarProps) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLanguageMenuOpen, setIsLanguageMenuOpen] = useState(false);
  const [isClient, setIsClient] = useState(false);
  const { language, setLanguage, t } = useLanguage();

  useEffect(() => {
    setIsClient(true);
  }, []);

  const handleMenuToggle = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const handleLanguageToggle = () => {
    setIsLanguageMenuOpen(!isLanguageMenuOpen);
  };

  const isActive = (page: string) => activePage === page;

  const handleLanguageChange = (lang: "en" | "es" | "ca") => {
    setLanguage(lang);
    setIsLanguageMenuOpen(false);
  };

  if (!isClient) {
    // Return a simplified version during SSR to prevent hydration issues
    return (
      <nav className="bg-card border-b border-border sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-6">
              <Link href="/" className="flex items-center">
                <Image
                  src="/images/the_news_hub_logo.png"
                  alt="The News Hub"
                  width={120}
                  height={40}
                  className="h-10 w-auto"
                  priority
                />
              </Link>
            </div>
          </div>
        </div>
      </nav>
    );
  }

  return (
    <nav className="bg-card border-b border-border sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Left side - Logo and Navigation options */}
          <div className="flex items-center space-x-6">
            <Link href="/" className="flex items-center">
              <Image
                src="/images/the_news_hub_logo.png"
                alt="The News Hub"
                width={120}
                height={40}
                className="h-10 w-auto"
                priority
              />
            </Link>
            <div className="hidden md:flex items-center space-x-1">
              <Link 
                href="/latest-news" 
                className={`px-4 py-2 rounded-full font-bold transition-colors ${
                  isActive("noticias")
                    ? "bg-[#f7c873] text-[#1a2238]"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {t("nav.latest-news")}
              </Link>
              <Link 
                href="/hot-topics" 
                className={`px-4 py-2 rounded-full font-bold transition-colors ${
                  isActive("tema-caliente")
                    ? "bg-[#f7c873] text-[#1a2238]"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {t("nav.hot-topics")}
              </Link>
              <Link 
                href="/askhub" 
                className={`px-4 py-2 rounded-full font-bold transition-colors ${
                  isActive("ia")
                    ? "bg-[#f7c873] text-[#1a2238]"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {t("nav.ai-chatbot")}
              </Link>
            </div>
          </div>

          {/* Right side - Language selector and Buttons */}
          <div className="hidden md:flex items-center space-x-3">
            {/* Language Selector */}
            <div className="relative">
              <button
                onClick={handleLanguageToggle}
                className="flex items-center space-x-1 px-3 py-2 text-foreground hover:text-primary transition-colors"
              >
                <Globe className="w-4 h-4" />
                <span className="text-sm font-bold">{language.toUpperCase()}</span>
              </button>
              
              {isLanguageMenuOpen && (
                <div className="absolute right-0 mt-2 w-28 bg-card border border-border rounded-lg shadow-lg z-50">
                  {/* <button
                    onClick={() => handleLanguageChange("es")}
                    className={`w-full px-3 py-2 text-left text-sm hover:bg-muted transition-colors ${
                      language === "es" ? "text-primary font-bold" : "text-foreground"
                    }`}
                  >
                    Español
                  </button>
                  <button
                    onClick={() => handleLanguageChange("ca")}
                    className={`w-full px-3 py-2 text-left text-sm hover:bg-muted transition-colors ${
                      language === "ca" ? "text-primary font-bold" : "text-foreground"
                    }`}
                  >
                    Català
                  </button> */}
                  <button
                    onClick={() => handleLanguageChange("en")}
                    className={`w-full px-3 py-2 text-left text-sm hover:bg-muted transition-colors ${
                      language === "en" ? "text-primary font-bold" : "text-foreground"
                    }`}
                  >
                    English
                  </button>
                </div>
              )}
            </div>
            
            {/* <button className="px-4 py-2 text-foreground hover:text-primary transition-colors font-medium">
              {t("nav.register")}
            </button> */}
            {/* <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium">
              {t("nav.login")}
            </button> */}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={handleMenuToggle}
              className="text-foreground hover:text-primary transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-card border-t border-border">
              <Link 
                href="/latest-news" 
                className={`block px-3 py-2 rounded-full font-medium transition-colors ${
                  isActive("noticias")
                    ? "bg-[#f7c873] text-[#1a2238]"
                    : "text-foreground hover:text-primary"
                }`}
              >
                {t("nav.latest-news")}
              </Link>
              <Link 
                href="/hot-topics" 
                className={`block px-3 py-2 rounded-full font-medium transition-colors ${
                  isActive("tema-caliente")
                    ? "bg-[#f7c873] text-[#1a2238]"
                    : "text-foreground hover:text-primary"
                }`}
              >
                {t("nav.hot-topics")}
              </Link>
              <Link 
                href="/askhub" 
                className={`block px-3 py-2 rounded-full font-medium transition-colors ${
                  isActive("ia")
                    ? "bg-[#f7c873] text-[#1a2238]"
                    : "text-foreground hover:text-primary"
                }`}
              >
                {t("nav.ai-chatbot")}
              </Link>
              <div className="pt-2 border-t border-border space-y-2">
                {/* Mobile Language Selector */}
                <div className="flex items-center justify-between px-3 py-2">
                  <span className="text-sm text-muted-foreground">Idioma:</span>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleLanguageChange("es")}
                      className={`px-2 py-1 text-xs rounded ${
                        language === "es" 
                          ? "bg-primary text-primary-foreground" 
                          : "bg-muted text-muted-foreground"
                      }`}
                    >
                      ES
                    </button>
                    <button
                      onClick={() => handleLanguageChange("ca")}
                      className={`px-2 py-1 text-xs rounded ${
                        language === "ca" 
                          ? "bg-primary text-primary-foreground" 
                          : "bg-muted text-muted-foreground"
                      }`}
                    >
                      CA
                    </button>
                    <button
                      onClick={() => handleLanguageChange("en")}
                      className={`px-2 py-1 text-xs rounded ${
                        language === "en" 
                          ? "bg-primary text-primary-foreground" 
                          : "bg-muted text-muted-foreground"
                      }`}
                    >
                      EN
                    </button>
                  </div>
                </div>
                <button className="w-full px-3 py-2 text-foreground hover:text-primary transition-colors font-medium">
                  {t("nav.register")}
                </button>
                <button className="w-full px-3 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium">
                  {t("nav.login")}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default NavigationBar; 