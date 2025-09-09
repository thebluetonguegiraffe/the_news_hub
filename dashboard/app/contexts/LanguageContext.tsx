"use client";

import React, { createContext, useContext, useState, ReactNode, useEffect } from "react";

type Language = "es" | "en" | "ca";

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// Translation dictionary
const translations = {
  es: {
    // Navigation
    "nav.latest-news": "Últimas Noticias",
    "nav.hot-topics": "Temas Calientes",
    "nav.ai-chatbot": "Chatbot IA",
    "nav.register": "Registrarse",
    "nav.login": "Acceder",
    
    // Home page
    "home.hero.title": "Bienvenido a The News Hub",
    "home.hero.subtitle": "Tu fuente confiable de noticias actualizadas, análisis profundo e interacción inteligente con IA para mantenerte informado del mundo que te rodea.",
    "home.hero.explore": "Explorar Noticias",
    "home.hero.try-ai": "Probar IA",
    
    // Features
    "features.title": "Características Principales",
    "features.subtitle": "Descubre todo lo que The News Hub tiene para ofrecerte",
    "features.news.title": "Titulares Actualizados",
    "features.news.description": "Accede a las últimas noticias y titulares de todo el mundo en tiempo real.",
    "features.topics.title": "Temas Calientes",
    "features.topics.description": "Descubre los temas más relevantes de la semana con análisis detallados.",
    "features.ai.title": "Interacción con IA",
    "features.ai.description": "Haz preguntas sobre noticias y obtén respuestas inteligentes y precisas.",
    
    // Benefits
    "benefits.title": "Beneficios para Ti",
    "benefits.subtitle": "Descubre por qué The News Hub es tu mejor opción para estar informado",
    "benefits.24h": "Información actualizada las 24 horas",
    "benefits.analysis": "Análisis profundo de temas relevantes",
    "benefits.ai": "Interacción inteligente con IA",
    "benefits.clean": "Interfaz limpia y fácil de usar",
    "benefits.verified": "Contenido verificado y confiable",
    "benefits.devices": "Acceso desde cualquier dispositivo",
    
    // CTA
    "cta.title": "¡Comienza tu Experiencia Hoy!",
    "cta.subtitle": "Regístrate o inicia sesión para personalizar tu experiencia y recibir noticias adaptadas a tus intereses.",
    "cta.register": "Registrarse",
    "cta.login": "Iniciar Sesión",
    
    // FAQ
    "faq.title": "Preguntas Frecuentes",
    "faq.subtitle": "Resolvemos tus dudas más comunes",
    "faq.ai.question": "¿Cómo funciona la interacción con IA?",
    "faq.ai.answer": "Nuestra IA te permite hacer preguntas sobre cualquier noticia y obtendrás respuestas inteligentes y precisas basadas en la información más actualizada.",
    "faq.updates.question": "¿Con qué frecuencia se actualizan las noticias?",
    "faq.updates.answer": "Las noticias se actualizan en tiempo real, 24 horas al día, 7 días a la semana para mantenerte siempre informado.",
    "faq.personalize.question": "¿Puedo personalizar las noticias que veo?",
    "faq.personalize.answer": "Sí, al registrarte puedes personalizar tus preferencias y recibir noticias adaptadas a tus intereses específicos.",
    "faq.free.question": "¿Es gratuito el acceso a The News Hub?",
    "faq.free.answer": "Sí, el acceso básico es completamente gratuito. Ofrecemos funciones premium para usuarios que deseen una experiencia más avanzada.",
    
    // Footer
    "footer.description": "Tu fuente confiable de noticias actualizadas y análisis profundo.",
    "footer.navigation": "Navegación",
    "footer.resources": "Recursos",
    "footer.follow": "Síguenos",
    "footer.copyright": "© 2024 The News Hub. Todos los derechos reservados.",
  },
  en: {
    // Navigation
    "nav.latest-news": "Latest News",
    "nav.hot-topics": "Hot Topics",
    "nav.ai-chatbot": "AskHub",
    "nav.register": "Register",
    "nav.login": "Login",
    
    // Home page
    "home.hero.title": "Welcome to The News Hub",
    "home.hero.subtitle": "Your reliable source for updated news, smart analysis, and AI-powered insights .",
    "home.hero.explore": "Explore Latest News",
    "home.hero.try-ai": "Try AskHub",
    
    // Features
    "features.title": "Main Features",
    "features.subtitle": "Discover everything The News Hub has to offer you",
    "features.news.title": "Updated Headlines",
    "features.news.description": "Access the latest news and headlines from around the world in real time.",
    "features.topics.title": "Hot Topics",
    "features.topics.description": "Discover the most relevant topics of the week with detailed analysis.",
    "features.ai.title": "AI Interaction",
    "features.ai.description": "Ask questions about news and get intelligent and accurate answers.",
    
    // Benefits
    "benefits.title": "Benefits for You",
    "benefits.subtitle": "Discover why The News Hub is your best option to stay informed",
    "benefits.24h": "24-hour updated information",
    "benefits.analysis": "In-depth analysis of relevant topics",
    "benefits.ai": "Intelligent AI interaction",
    "benefits.clean": "Clean and easy-to-use interface",
    "benefits.verified": "Verified and reliable content",
    "benefits.devices": "Access from any device",
    
    // CTA
    "cta.title": "Start Your Experience Today!",
    "cta.subtitle": "Register or log in to personalize your experience and receive news tailored to your interests.",
    "cta.register": "Register",
    "cta.login": "Login",
    
    // FAQ
    "faq.title": "Frequently Asked Questions",
    "faq.subtitle": "We answer your most common questions",
    "faq.ai.question": "How does AI interaction work?",
    "faq.ai.answer": "Ask about any topic — our AI delivers smart, accurate answers using the most up-to-date news.",
    "faq.updates.question": "How often are news updated?",
    "faq.updates.answer": "News is updated in real time, 24 hours a day, 7 days a week to keep you always informed.",
    "faq.personalize.question": "Can I personalize the news I see?",
    "faq.personalize.answer": "Yes, when you register you can personalize your preferences and receive news adapted to your specific interests.",
    "faq.free.question": "Is access to The News Hub free?",
    "faq.free.answer": "Yes, basic access is completely free. We offer premium features for users who want a more advanced experience.",
    
    // Footer
    "footer.description": "Stay informed with AI-powered news and insights.",
    "footer.navigation": "Navigation",
    "footer.resources": "Resources",
    "footer.follow": "Follow Us",
    "footer.copyright": "© All rights reserved.",
  },
  ca: {
    // Navigation
    "nav.latest-news": "Últimes Notícies",
    "nav.hot-topics": "Temes Candents",
    "nav.ai-chatbot": "Chatbot IA",
    "nav.register": "Registrar-se",
    "nav.login": "Accedir",
    
    // Home page
    "home.hero.title": "Benvingut a The News Hub",
    "home.hero.subtitle": "La teva font fiable de notícies actualitzades, anàlisi profunda i interacció intel·ligent amb IA per mantenir-te informat del món que t'envolta.",
    "home.hero.explore": "Explorar Notícies",
    "home.hero.try-ai": "Provar IA",
    
    // Features
    "features.title": "Característiques Principals",
    "features.subtitle": "Descobreix tot el que The News Hub té per oferir-te",
    "features.news.title": "Titulars Actualitzats",
    "features.news.description": "Accedeix a les últimes notícies i titulars de tot el món en temps real.",
    "features.topics.title": "Temes Candents",
    "features.topics.description": "Descobreix els temes més rellevants de la setmana amb anàlisi detallada.",
    "features.ai.title": "Interacció amb IA",
    "features.ai.description": "Fes preguntes sobre notícies i obtén respostes intel·ligents i precises.",
    
    // Benefits
    "benefits.title": "Beneficis per a Tu",
    "benefits.subtitle": "Descobreix per què The News Hub és la teva millor opció per estar informat",
    "benefits.24h": "Informació actualitzada les 24 hores",
    "benefits.analysis": "Anàlisi profunda de temes rellevants",
    "benefits.ai": "Interacció intel·ligent amb IA",
    "benefits.clean": "Interfície neta i fàcil d'usar",
    "benefits.verified": "Contingut verificat i fiable",
    "benefits.devices": "Accés des de qualsevol dispositiu",
    
    // CTA
    "cta.title": "¡Comença la teva Experiència Avui!",
    "cta.subtitle": "Registra't o inicia sessió per personalitzar la teva experiència i rebre notícies adaptades als teus interessos.",
    "cta.register": "Registrar-se",
    "cta.login": "Iniciar Sessió",
    
    // FAQ
    "faq.title": "Preguntes Freqüents",
    "faq.subtitle": "Resolem les teves dubtes més comunes",
    "faq.ai.question": "Com funciona la interacció amb IA?",
    "faq.ai.answer": "La nostra IA et permet fer preguntes sobre qualsevol notícia i obtindràs respostes intel·ligents i precises basades en la informació més actualitzada.",
    "faq.updates.question": "Amb quina freqüència s'actualitzen les notícies?",
    "faq.updates.answer": "Les notícies s'actualitzen en temps real, 24 hores al dia, 7 dies a la setmana per mantenir-te sempre informat.",
    "faq.personalize.question": "Puc personalitzar les notícies que veig?",
    "faq.personalize.answer": "Sí, en registrar-te pots personalitzar les teves preferències i rebre notícies adaptades als teus interessos específics.",
    "faq.free.question": "És gratuït l'accés a The News Hub?",
    "faq.free.answer": "Sí, l'accés bàsic és completament gratuït. Oferim funcions premium per a usuaris que desitgin una experiència més avançada.",
    
    // Footer
    "footer.description": "La teva font fiable de notícies actualitzades i anàlisi profunda.",
    "footer.navigation": "Navegació",
    "footer.resources": "Recursos",
    "footer.follow": "Segueix-nos",
    "footer.copyright": "© 2024 The News Hub. Tots els drets reservats.",
  },
};

export const LanguageProvider = ({ children }: { children: ReactNode }) => {
  const [language, setLanguage] = useState<Language>("en");
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const t = (key: string): string => {
    if (!isClient) {
      // Return English translations during SSR to prevent hydration mismatch
      return translations.en[key as keyof typeof translations.en] || key;
    }
    return translations[language][key as keyof typeof translations[typeof language]] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
}; 