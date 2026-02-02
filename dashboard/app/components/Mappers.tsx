import {
  // Original & General
  Globe, ShieldCheck, BarChart2, Building2, Microscope, Zap, Heart, Leaf,
  Globe2, Trophy, Music, BookOpen, AlertTriangle, Users,

  // New Imports
  Scale, Flame, RefreshCw, Network, Landmark, Gavel, Swords, Car,
  Briefcase, DollarSign, HeartHandshake, Ship,
  Megaphone, CloudRain, Bomb, Truck, Battery, Factory, Rainbow,
  Tv, Lock, PawPrint, EyeOff, TrendingUp, Tractor, Dna, Palette,
  Home, ShoppingBag, Plane, Church, SearchX, Utensils, Radio,
  ShieldAlert, Accessibility, Tent, FileText, Rocket, Droplets,
  History, MapPin, Smile, Ticket, MessageSquare, Building,

  // Fallback Icon
  CircleHelp,
  Scroll
} from 'lucide-react';

// Define the map
const iconMap: Record<string, React.ComponentType<any>> = {
  // --- Professional Human Rights & Law ---
  "human rights": Scale,        // Professional/Justice focus
  law: Gavel,
  legal: Scroll,
  justice: ShieldCheck,
  policy: FileText,
  administration: Landmark,
  diplomacy: HeartHandshake,

  // --- Original icons ---
  politics: Globe,
  government: ShieldCheck,
  economy: BarChart2,
  business: Building2,
  science: Microscope,
  technology: Zap,
  health: Heart,
  environment: Leaf,
  "world News": Globe2,
  sports: Trophy,
  sport: Trophy,
  arts: Music,
  culture: BookOpen,
  crime: AlertTriangle,
  "public Safety": Users,

  // --- Society & Conflict ---
  society: Users,
  lgbtq: Rainbow,
  disability: Accessibility,
  homelessness: Tent,
  migration: Ship,
  discrimination: SearchX,
  disparities: Scale,
  conflict: Swords,
  dispute: MessageSquare,
  disputes: MessageSquare,
  violence: Bomb,
  terrorism: ShieldAlert,
  security: Lock,
  cybersecurity: ShieldCheck,
  military: Swords,
  disinformation: EyeOff,

  // --- Disasters & Resources ---
  disasters: Flame,
  disaster: Flame,
  accidents: AlertTriangle,
  safety: ShieldCheck,
  theft: AlertTriangle,
  climate: CloudRain,
  water: Droplets,
  agriculture: Tractor,
  animal: PawPrint,
  food: Utensils,

  // --- Economy & Industry ---
  finance: DollarSign,
  trade: Ship,
  commerce: ShoppingBag,
  industry: Factory,
  labor: Briefcase,
  employment: Briefcase,
  restructuring: RefreshCw,
  corporate: Building2,
  advertising: Megaphone,

  // --- Science & Infrastructure ---
  "public health": Heart,
  publichealth: Heart,
  biology: Dna,
  spaceflight: Rocket,
  energy: Battery,
  power: Zap,
  transport: Truck,
  automotive: Car,
  urbanization: Building,
  housing: Home,
  development: TrendingUp,

  // --- Media & Lifestyle ---
  media: Tv,
  journalism: Radio,
  disclosure: FileText,
  disruption: Zap,
  art: Palette,
  religion: Church,
  history: History,
  lifestyle: Smile,
  travel: Plane,
  settlements: MapPin,
  lottery: Ticket,
  geopolitics: Network,
  discourse: MessageSquare,
};

export const getTopicIcon = (topicId: string) => {
  return iconMap[topicId] || CircleHelp;
};

const AVAILABLE_SOURCES = [
  { id: "https://www.lavanguardia.com/", name: "La Vanguardia", icon: "/images/la-vanguardia.png" },
  { id: "https://www.ara.cat/", name: "Ara", icon: "/images/ara.png" },
  { id: "www.washingtonpost.com", name: "The Washington Post", icon: "/images/WP.png" },
  { id: "www.nytimes.com", name: "The New York Times", icon: "/images/nyt.png" },
  { id: "www.bbc.com", name: "BBC News", icon: "/images/BBC.jpg" },
  { id: "www.theguardian.com", name: "The Guardian", icon: "/images/the_guardian.jpg" },
  { id: "https://elpais.com/", name: "El País", icon: "/images/el-país.png" },
  { id: "https://www.elperiodico.com/es/", name: "El Periodico", icon: "/images/el-periodico.png" },
];

export { AVAILABLE_SOURCES };
export default iconMap;