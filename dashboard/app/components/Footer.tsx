import Image from "next/image";
import { useLanguage } from "../contexts/LanguageContext";

import logoImg from "../../public/images/the_news_hub_logo.png";

const Footer = () => {
  const { t } = useLanguage();

  return (
    <footer className="bg-card border-t border-border py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center w-full gap-8">
          
          <div className="flex items-center gap-3">
            <div className="relative w-8 h-8">
              <Image
                src={logoImg} 
                alt=""
                width={32}
                height={32}
                className="object-contain"
                priority
              />
            </div>
            <h3 className="text-lg font-bold text-foreground">
              The News Hub
            </h3>
          </div>

          <div className="flex flex-col md:flex-row gap-4 md:gap-8 items-center text-center">
            <p className="text-muted-foreground text-sm">
              {t("footer.description")}
            </p>
            <p className="text-muted-foreground text-sm italic">
              {t("footer.copyright")}
            </p>
          </div>

          <div className="flex items-center gap-6">
            <a
              href="https://github.com/thebluetonguegiraffe/the_news_hub"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-foreground transition-colors"
              aria-label="GitHub Repository"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.041-1.61-4.041-1.61-.546-1.387-1.333-1.756-1.333-1.756-1.089-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28 1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.362.81 1.096.81 2.22v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
              </svg>
            </a>

            <a
              href="mailto:thebluetonguegiraffe+dev@gmail.com"
              className="flex items-center text-muted-foreground hover:text-[#f7c873] transition-colors"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;