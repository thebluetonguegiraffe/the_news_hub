
import Image from "next/image";
import { useLanguage } from "../contexts/LanguageContext";
import Link from "next/link";
import { Users } from "lucide-react";

const Footer = () => {
    const { t } = useLanguage();
    
    return (
      <footer className="bg-card border-t border-border py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
                <Image
                  src="/images/the_news_hub_logo.png"
                  alt="The News Hub"
                  width={32}
                  height={32}
                  className="h-8 w-auto"
                />
                The News Hub
              </h3>
              <p className="text-muted-foreground">
                {t("footer.description")}
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold text-foreground mb-4 flex items-center gap-2">
                <div className="w-2 h-2 bg-[#f7c873] rounded-full"></div>
                {t("footer.navigation")}
              </h4>
              <ul className="space-y-2">
                <li><Link href="/" className="text-muted-foreground hover:text-[#f7c873] transition-colors">Home</Link></li>
                <li><Link href="/latest-news" className="text-muted-foreground hover:text-[#f7c873] transition-colors">Latest News</Link></li>
                <li><Link href="/hot-topics" className="text-muted-foreground hover:text-[#f7c873] transition-colors">Hot Topics</Link></li>
                <li><Link href="/askhub" className="text-muted-foreground hover:text-[#f7c873] transition-colors">AskHub</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-foreground mb-4 flex items-center gap-2">
                <div className="w-2 h-2 bg-[#f7c873] rounded-full"></div>
                {t("footer.resources")}
              </h4>
              <ul className="space-y-2">
                <li>
                  <a href="#" className="flex items-center text-muted-foreground hover:text-[#f7c873] transition-colors">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                    </svg>
                    Blog
                  </a>
                </li>
                <li>
                  <a href="#" className="flex items-center text-muted-foreground hover:text-[#f7c873] transition-colors">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Help
                  </a>
                </li>
                <li>
                  <a href="#" className="flex items-center text-muted-foreground hover:text-[#f7c873] transition-colors">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    Contact
                  </a>
                </li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-foreground mb-4 flex items-center gap-2">
                <div className="w-2 h-2 bg-[#f7c873] rounded-full"></div>
                {t("footer.follow")}
              </h4>
              <div className="flex space-x-4">
                <a href="#" className="text-muted-foreground hover:text-[#f7c873] transition-colors">
                  <Users className="w-5 h-5" />
                </a>
              </div>
            </div>
          </div>
          
          <div className="border-t border-border mt-8 pt-8 text-center">
            <p className="text-muted-foreground">
              {t("footer.copyright")}
            </p>
          </div>
        </div>
      </footer>
    );
  };

export default Footer; 