"use client";

import React, { createContext, useContext, useState, ReactNode, useEffect } from "react";

type Language = "es" | "en" | "ca";

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string, args?: Record<string, string | number>) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// Translation dictionary
const translations = {
  es: {
    // Navigation
    "nav.latest-news": "Últimas Noticias",
    "nav.hot-topics": "Tendencias",
    "nav.ai-chatbot": "AskHub",
    "nav.register": "Registrarse",
    "nav.login": "Acceder",

    // Hot Topics Page
    "hot_topics.hero.tagline": "Está pasando",
    "hot_topics.hero.subtitle": "Descubre los temas más actuales.",
    "hot_topics.list.title": "Temas",
    "hot_topics.no_topics.title": "No hay temas registrados durante este rango de fechas",
    "hot_topics.no_topics.message": "Por favor, selecciona un rango de fechas diferente.",
    "hot_topics.card.news_count": "noticias",
    "hot_topics.card.read_more": "Ver Más",

    // Topics Chart
    "topics_chart.title": "Evolución de los {count} temas más populares de la semana",
    "topics_chart.no_data": "Sin datos",
    "topics_chart.total_news": "noticias totales",
    "topics_chart.docs": "Docs",

    // Topic Page
    "topic_page.filters": "Filtros",
    "topic_page.back": "Volver a Tendencias",

    // AskHub Page
    "askhub.hero.pill": "Aprende sobre todo",
    "askhub.hero.subtitle": "Haz preguntas sobre cualquier tema de actualidad y obtén respuestas inteligentes y precisas impulsadas por tecnología de IA avanzada.",
    "askhub.search.placeholder": "Pregunta sobre cualquier tema, eventos o noticia...",
    "askhub.search.button.searching": "Buscando...",
    "askhub.search.button.default": "Preguntar",

    "askhub.results.searching_for": "Buscando",
    "askhub.results.analyzing": "Nuestra IA está analizando las últimas noticias y encontrando los artículos más relevantes para ti",
    "askhub.results.title": "Resultados de búsqueda para",
    "askhub.results.summary": "Resumen",
    "askhub.results.read_more": "Leer Más",

    "askhub.how.title": "Cómo funciona",
    "askhub.how.subtitle": "Obtén respuestas inteligentes sobre la actualidad en tres sencillos pasos",
    "askhub.how.step1.title": "Haz tu pregunta",
    "askhub.how.step1.desc": "Escribe sobre cualquier tema o noticia que quieras explorar.",
    "askhub.how.step2.title": "Análisis inteligente",
    "askhub.how.step2.desc": "Nuestros modelos de Machine Learning y de Lenguaje procesa las fuentes para identificar la información más relevante.",
    "askhub.how.step3.title": "Respuestas con contexto",
    "askhub.how.step3.desc": "Obtiene resúmenes precisos y actualizados con acceso directo a las fuentes originales.",

    // Latest News Page
    "latest_news.hero.tagline": "Noticias impulsadas por IA",
    "latest_news.hero.subtitle": "Mantente informado con las últimas noticias.",
    "latest_news.filters.title": "Filtros",
    "latest_news.loading": "Cargando historias más recientes...",

    // News Filter
    "news_filter.sources": "Fuentes",
    "news_filter.topics": "Temas",
    "news_filter.select_all": "Seleccionar todo",
    "news_filter.clear": "Limpiar",

    // News List
    "news_list.no_articles": "No se encontraron artículos.",
    "news_list.read_more": "Leer noticia completa",
    "news_list.source_default": "Fuente de noticias",

    // Dates
    "dates.today": "Hoy",
    "dates.yesterday": "Ayer",
    "dates.days_ago": "Hace {count} días",
    "dates.mon": "Lu",
    "dates.tue": "Ma",
    "dates.wed": "Mi",
    "dates.thu": "Ju",
    "dates.fri": "Vi",
    "dates.sat": "Sa",
    "dates.sun": "Do",

    // Home page
    "home.hero.tagline": "Noticias impulsadas por IA",
    "home.hero.welcome": "Bienvenido a",
    "home.hero.brand": "The News Hub",
    "home.hero.subtitle": "Tu fuente de noticias y análisis inteligente para comprender el mundo actual.",
    "home.hero.explore": "Explorar Noticias",
    "home.hero.try-ai": "Probar AskHub",

    // Features
    "features.title": "Características Principales",
    "features.subtitle": "Descubre todo lo que The News Hub tiene para ofrecerte",
    "features.news.title": "Titulares Actualizados",
    "features.news.description": "Accede a las últimas noticias y titulares de todo el mundo en tiempo real.",
    "features.topics.title": "Tendencias",
    "features.topics.description": "Descubre los temas más relevantes de la semana con análisis detallados.",
    "features.ai.title": "Interacción con AskHub",
    "features.ai.description": "La actualidad al alcance de tu mano: pregunta lo que quieras y comprende el mundo que te rodea.",

    // Sources
    "sources.title": "Nuestras Fuentes",
    "sources.subtitle": "Contamos con las organizaciones de noticias más reputadas del mundo para brindarte una cobertura precisa, oportuna y completa.",
    "sources.twp.description": "Periódico estadounidense de referencia que destaca por su transparencia y rigor.",
    "sources.nyt.description": "Periódico internacional de referencia que destaca por su cobertura objetiva.",
    "sources.bbc.description": "Periodico británico conocido por su cobertura internacional extensiva.",
    "sources.guardian.description": "Periodico independiente famoso por sus investigaciones profundas en amplios temas.",
    "sources.ara.description": "Periódico catalán de referencia conocido por sus reportajes independientes.",
    "sources.lavanguardia.description": "Diario español con cobertura extensa nacional y global.",
    "sources.elpais.description": "Diario global en español, referente en actualidad de España y América Latina.",
    "sources.elperiodico.description": "Diario generalista editado en Barcelona con foco en actualidad catalana y española.",
    // FAQ
    "faq.title": "Preguntas Frecuentes",
    "faq.ai.question": "¿Cómo funciona AskHub?",
    "faq.ai.answer": "Haz una pregunta en AskHub y el sistema seleccionará los artículos más relevantes para generar un resumen, mostrándote también las fuentes originales.",
    "faq.updates.question": "¿Con qué frecuencia se actualizan las noticias?",
    "faq.updates.answer": "Las noticias se actualizan dos veces al día para garantizar información precisa y reciente. El nuevo contenido se publica cada día a mediodía y a medianoche.",
    "faq.personalize.question": "¿Cómo se determinan los temas de tendencia?",
    "faq.personalize.answer": "Los temas se extraen mediante un algoritmo de aprendizaje automático que agrupa noticias similares y asigna a cada grupo un tema relevante.",
    "faq.free.question": "¿Puedo personalizar las noticias que veo en The News Hub?",
    "faq.free.answer": "Sí, puedes personalizar tu experiencia seleccionando tus fuentes preferidas para que The News Hub te muestre el contenido que más te interesa.",

    // Footer
    "footer.description": "Tu fuente confiable de noticias actualizadas y análisis profundo.",
    "footer.navigation": "Navegación",
    "footer.resources": "Recursos",
    "footer.follow": "Síguenos",
    "footer.copyright": "© 2025 The News Hub. Todos los derechos reservados.",
    "askhub.error.rate_limit_title": "Límite Alcanzado",
    "askhub.error.rate_limit_msg": "Has alcanzado el límite gratuito para esta demostración ({max} peticiones/hora). Por favor, inténtalo más tarde.",
  },
  en: {
    // Navigation
    "nav.latest-news": "Latest News",
    "nav.hot-topics": "Hot Topics",
    "nav.ai-chatbot": "AskHub",
    "nav.register": "Register",
    "nav.login": "Login",

    // Hot Topics Page
    "hot_topics.hero.tagline": "Trending Now",
    "hot_topics.hero.subtitle": "Discover the most trending topics and breaking stories.",
    "hot_topics.list.title": "Topics List",
    "hot_topics.no_topics.title": "No topics registered during this range of dates",
    "hot_topics.no_topics.message": "Please select a different range of dates.",
    "hot_topics.card.news_count": "news",
    "hot_topics.card.read_more": "See More",

    // Topics Chart
    "topics_chart.title": "Weekly top-{count} most popular topics evolution",
    "topics_chart.no_data": "No Data",
    "topics_chart.total_news": "total news items",
    "topics_chart.docs": "Docs",

    // Topic Page
    "topic_page.filters": "Filters",
    "topic_page.back": "Go back to Hot Topics",

    // AskHub Page
    "askhub.hero.pill": "Learn about everything",
    "askhub.hero.subtitle": "Ask questions about any news topic and get intelligent, accurate answers powered by advanced AI technology.",
    "askhub.search.placeholder": "Ask about any topic, current events, or breaking news...",
    "askhub.search.button.searching": "Searching...",
    "askhub.search.button.default": "Ask",

    "askhub.results.searching_for": "Searching for",
    "askhub.results.analyzing": "Our AI is analyzing the latest news and finding the most relevant articles for you",
    "askhub.results.title": "Search Results for",
    "askhub.results.summary": "Summary",
    "askhub.results.read_more": "Read More",

    "askhub.how.title": "How it works",
    "askhub.how.subtitle": "Get smart answers to your news questions in three simple steps",
    "askhub.how.step1.title": "Ask your question",
    "askhub.how.step1.desc": "Type in any topic or news story you want to explore.",
    "askhub.how.step2.title": "Smart analysis",
    "askhub.how.step2.desc": "Our Machine and Language Models process the sources to identify the most relevant information.",
    "askhub.how.step3.title": "Contextual answers",
    "askhub.how.step3.desc": "Get accurate, up-to-date summaries with direct access to the original sources.",

    // Latest News Page
    "latest_news.hero.tagline": "AI-Powered News",
    "latest_news.hero.subtitle": "Stay informed with the latest news and breaking stories.",
    "latest_news.filters.title": "Filters",
    "latest_news.loading": "Loading latest stories...",

    // News Filter
    "news_filter.sources": "Sources",
    "news_filter.topics": "Topics",
    "news_filter.select_all": "Select All",
    "news_filter.clear": "Clear",

    // News List
    "news_list.no_articles": "No articles found.",
    "news_list.read_more": "Read Full Story",
    "news_list.source_default": "News Source",

    // Dates
    "dates.today": "Today",
    "dates.yesterday": "Yesterday",
    "dates.days_ago": "{count} days ago",
    "dates.mon": "Mo",
    "dates.tue": "Tu",
    "dates.wed": "We",
    "dates.thu": "Th",
    "dates.fri": "Fr",
    "dates.sat": "Sa",
    "dates.sun": "Su",

    // Home page
    "home.hero.tagline": "AI-Powered News",
    "home.hero.welcome": "Welcome to",
    "home.hero.brand": "The News Hub",
    "home.hero.subtitle": "Your reliable source for updated news and smart analysis to understand todays world.",
    "home.hero.explore": "Explore Latest News",
    "home.hero.try-ai": "Try AskHub",

    // Features
    "features.title": "Main Features",
    "features.subtitle": "Discover everything The News Hub has to offer you",
    "features.news.title": "Updated Headlines",
    "features.news.description": "Access the latest news and headlines from around the world in real time.",
    "features.topics.title": "Hot Topics",
    "features.topics.description": "Discover the most relevant topics of the week.",
    "features.ai.title": "AskHub Interaction",
    "features.ai.description": "Trends at your fingertips: get the answers you need to understand today's world.",

    // Sources
    "sources.title": "Our Trusted Sources",
    "sources.subtitle": "We partner with the world's most reputable news organizations to bring you accurate, timely, and comprehensive coverage.",
    "sources.twp.description": "A leader in political journalism and government accountability with exceptional rigor.",
    "sources.nyt.description": "A global benchmark for in-depth analysis, culture, and high-quality reporting.",
    "sources.bbc.description": "A world leader in international news, renowned for its neutrality and global reach.",
    "sources.guardian.description": "Independent investigative journalism committed to social and global issues.",
    "sources.ara.description": "Cutting-edge Catalan journalism focused on independent analysis and opinion.",
    "sources.lavanguardia.description": "A historic newspaper offering a balanced view of national and international affairs.",
    "sources.elpais.description": "Leading global Spanish-language newspaper covering Spain and Latin America.",
    "sources.elperiodico.description": "Barcelona-based daily newspaper focusing on Catalan and Spanish current affairs.",

    // FAQ
    "faq.title": "Frequently Asked Questions",
    "faq.ai.question": "How does AskHub work?",
    "faq.ai.answer": "Introduce a question in Askhub. It will select articles relevant to your question and generate a summary of them, while also displaying the articles to you.",
    "faq.updates.question": "How often are news updated?",
    "faq.updates.answer": "The news is updated twice daily to ensure timely and accurate information. New content is published every day at noon and again at midnight.",
    "faq.personalize.question": "How are hot topics determined?",
    "faq.personalize.answer": "Topics are extracted using a machine learning algorithm that groups similar news items together and assigns each group a relevant topic.",
    "faq.free.question": "Can I customize the news I see on The News Hub?",
    "faq.free.answer": "Yes, users can personalize their experience by selecting preferred news sources, allowing The News Hub to display more relevant content.",

    // Footer
    "footer.description": "Stay informed with AI-powered news and insights.",
    "footer.navigation": "Navigation",
    "footer.resources": "Resources",
    "footer.follow": "Follow Us",
    "footer.copyright": "© All rights reserved.",
    "askhub.error.rate_limit_title": "Limit Reached",
    "askhub.error.rate_limit_msg": "You have reached the free limit for this demo ({max} requests/hour). Please try again later.",
  },
  ca: {
    // Navigation
    "nav.latest-news": "Últimes Notícies",
    "nav.hot-topics": "Tendències",
    "nav.ai-chatbot": "AskHub",
    "nav.register": "Registrar-se",
    "nav.login": "Accedir",

    // Hot Topics Page
    "hot_topics.hero.tagline": "Està passant",
    "hot_topics.hero.subtitle": "Descobreix els temes més actuals.",
    "hot_topics.list.title": "Temes",
    "hot_topics.no_topics.title": "No hi ha temes registrats durant aquest rang de dates",
    "hot_topics.no_topics.message": "Si us plau, selecciona un rang de dates diferent.",
    "hot_topics.card.news_count": "notícies",
    "hot_topics.card.read_more": "Veure'n Més",

    // Topics Chart
    "topics_chart.title": "Evolució dels {count} temes més populars de la setmana",
    "topics_chart.no_data": "Sense dades",
    "topics_chart.total_news": "notícies totals",
    "topics_chart.docs": "Docs",

    // Topic Page
    "topic_page.filters": "Filtres",
    "topic_page.back": "Tornar a Tendències",

    // AskHub Page
    "askhub.hero.pill": "Aprèn sobre tot",
    "askhub.hero.subtitle": "Fes preguntes sobre qualsevol tema d'actualitat i obté respostes intel·ligents i precises impulsades per tecnologia d'IA avançada.",
    "askhub.search.placeholder": "Pregunta sobre qualsevol tema, esdeveniment o notícia...",
    "askhub.search.button.searching": "Cercant...",
    "askhub.search.button.default": "Preguntar",

    "askhub.results.searching_for": "Cercant",
    "askhub.results.analyzing": "La nostra IA està analitzant les últimes notícies i trobant els articles més rellevants per a tu",
    "askhub.results.title": "Resultats de cerca per a",
    "askhub.results.summary": "Resum",
    "askhub.results.read_more": "Llegir Més",

    "askhub.how.title": "Com funciona",
    "askhub.how.subtitle": "Obtén respostes intel·ligents sobre l'actualitat en tres senzills passos",
    "askhub.how.step1.title": "Fes la teva pregunta",
    "askhub.how.step1.desc": "Escriu sobre qualsevol tema o notícia que vulguis explorar.",
    "askhub.how.step2.title": "Anàlisi intel·ligent",
    "askhub.how.step2.desc": "Els nostres models de Llenguatge i Machine Learning processen les fonts per identificar la informació més rellevant.",
    "askhub.how.step3.title": "Respostes amb context",
    "askhub.how.step3.desc": "Rep resums precisos i actualitzats amb accés directe a les fonts originals.",

    // Latest News Page
    "latest_news.hero.tagline": "Notícies impulsades per IA",
    "latest_news.hero.subtitle": "Mantén-te informat amb les últimes notícies",
    "latest_news.filters.title": "Filtres",
    "latest_news.loading": "Carregant les notícies més recents...",

    // News Filter
    "news_filter.sources": "Fonts",
    "news_filter.topics": "Temes",
    "news_filter.select_all": "Seleccionar tot",
    "news_filter.clear": "Netejar",

    // News List
    "news_list.no_articles": "No s'han trobat articles.",
    "news_list.read_more": "Llegir notícia completa",
    "news_list.source_default": "Font de notícies",

    // Dates
    "dates.today": "Avui",
    "dates.yesterday": "Ahir",
    "dates.days_ago": "Fa {count} dies",
    "dates.mon": "Dl",
    "dates.tue": "Dt",
    "dates.wed": "Dc",
    "dates.thu": "Dj",
    "dates.fri": "Dv",
    "dates.sat": "Ds",
    "dates.sun": "Dg",

    // Home page
    "home.hero.tagline": "Notícies impulsades per IA",
    "home.hero.welcome": "Benvingut a",
    "home.hero.brand": "The News Hub",
    "home.hero.subtitle": "La teva font de notícies i anàlisi intel·ligent per comprendre el món actual.",
    "home.hero.explore": "Explorar Notícies",
    "home.hero.try-ai": "Provar AskHub",

    // Features
    "features.title": "Característiques Principals",
    "features.subtitle": "Descobreix tot el que The News Hub t'ofereix",
    "features.news.title": "Titulars Actualitzats",
    "features.news.description": "Accedeix a les últimes notícies i titulars de tot el món en temps real.",
    "features.topics.title": "Tendències",
    "features.topics.description": "Descobreix els temes més rellevants de la setmana.",
    "features.ai.title": "Interacció amb AskHub",
    "features.ai.description": "L’actualitat al teu abast: pregunta el que vulguis i entén el món que t'envolta.",

    // Sources
    "sources.title": "Les nostres fonts",
    "sources.subtitle": "Comptem amb les organitzacions de notícies més reputades del món per oferir-te una cobertura precisa, immediata i completa.",
    "sources.twp.description": "Líder en periodisme polític i fiscalització del poder amb un rigor excepcional.",
    "sources.nyt.description": "Referent global en anàlisi profunda, cultura i periodisme d'alta qualitat.",
    "sources.bbc.description": "Líder mundial en notícies internacionals, reconegut per la seva neutralitat i abast global.",
    "sources.guardian.description": "Periodisme independent d'investigació compromès amb temes socials i globals.",
    "sources.ara.description": "Periodisme català d'avantguarda centrat en l'anàlisi i l'opinió independent.",
    "sources.lavanguardia.description": "Diari històric amb una mirada equilibrada de l'actualitat nacional i internacional.",
    "sources.elpais.description": "Diari global en espanyol, referent en actualitat d'Espanya i Amèrica Llatina.",
    "sources.elperiodico.description": "Diari generalista editat a Barcelona amb focus en actualitat catalana i espanyola.",

    // FAQ
    "faq.title": "Preguntes Freqüents",
    "faq.ai.question": "Com funciona AskHub?",
    "faq.ai.answer": "Fes una pregunta a AskHub i el sistema seleccionarà els articles més rellevants per generar un resum, mostrant-te també les fonts originals.",
    "faq.updates.question": "Amb quina freqüència s'actualitzen les notícies?",
    "faq.updates.answer": "Les notícies s'actualitzen dues vegades al dia per garantir informació precisa i recent. El nou contingut es publica cada dia al migdia i a la mitjanit.",
    "faq.personalize.question": "Com es determinen els temes de tendència?",
    "faq.personalize.answer": "Els temes s'extreuen mitjançant un algorisme d'aprenentatge automàtic que agrupa notícies similars i assigna a cada grup un tema rellevant.",
    "faq.free.question": "Puc personalitzar les notícies que veig a The News Hub?",
    "faq.free.answer": "Sí, pots personalitzar la teva experiència seleccionant les teves fonts preferides perquè The News Hub et mostri el contingut que més t'interessa.",

    // Footer
    "footer.description": "La teva font fiable de notícies actualitzades i anàlisi profunda.",
    "footer.navigation": "Navegació",
    "footer.resources": "Recursos",
    "footer.follow": "Segueix-nos",
    "footer.copyright": "© 2025 The News Hub. Tots els drets reservats.",
    "askhub.error.rate_limit_title": "Límit Assolit",
    "askhub.error.rate_limit_msg": "Has assolit el límit gratuït per a aquesta demostració ({max} peticions/hora). Si us plau, torna-ho a provar més tard.",
  },
};

export const LanguageProvider = ({ children }: { children: ReactNode }) => {
  const [language, setLanguageState] = useState<Language>("en");
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("language") as Language;
    if (saved && ["es", "en", "ca"].includes(saved)) {
      setLanguageState(saved);
    }
    setIsClient(true);
  }, []);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem("language", lang);
  };

  const t = (key: string, args?: Record<string, string | number>): string => {
    if (!isClient) {
      // Return English translations during SSR to prevent hydration mismatch
      let text = translations.en[key as keyof typeof translations.en] || key;
      if (args) {
        Object.entries(args).forEach(([k, v]) => {
          text = text.replace(`{${k}}`, String(v));
        });
      }
      return text;
    }
    let text = translations[language][key as keyof typeof translations[typeof language]] || key;
    if (args) {
      Object.entries(args).forEach(([k, v]) => {
        text = text.replace(`{${k}}`, String(v));
      });
    }
    return text;
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