export interface Article {
  id: number;
  title: string;
  excerpt: string;
  topic: string;
  source: string;
  date: string;
  image: string;
  url: string;
}

export function getDaysFromDate(dateString: string, t: (key: string, args?: Record<string, string | number>) => string): string {
  const givenDate = new Date(dateString);
  const today = new Date();

  givenDate.setHours(0, 0, 0, 0);
  today.setHours(0, 0, 0, 0);

  const diffTime = today.getTime() - givenDate.getTime();
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return t("dates.today");
  if (diffDays === 1) return t("dates.yesterday");

  return t("dates.days_ago", { count: diffDays });
}


