"use client";

import React, { useMemo, useState } from 'react';
import {
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    BarChart,
    Bar,
    Cell
} from 'recharts';
import { TrendingUp } from 'lucide-react';
import iconMap from "./Mappers";
import { useLanguage } from "../contexts/LanguageContext";

const TOP_N = 12;
const defaultIcon = TrendingUp;
const PRIMARY_YELLOW = '#f7c873';

interface TopicEntry {
    date: string;
    docs_number: number;
}

interface Topic {
    _id: string;
    name: string;
    topic_es?: string;
    topic_ca?: string;
    topics_per_day: TopicEntry[] | Record<string, number> | null;
}

interface TopicsChartProps {
    rawData: Topic[];
}

const TopicsChart = ({ rawData }: TopicsChartProps) => {
    const { t, language } = useLanguage();
    const [activeTab, setActiveTab] = useState(0);

    const emptyTopic = useMemo(() => {
        const history = [];
        const today = new Date();
        for (let i = 6; i >= 0; i--) {
            const d = new Date(today);
            d.setDate(today.getDate() - i);
            let dateStr = d.toLocaleDateString(language, { weekday: 'short', day: 'numeric' });
            dateStr = dateStr.charAt(0).toUpperCase() + dateStr.slice(1).replace(" de ", " ").replace(" del ", " ");
            history.push({
                date: dateStr,
                value: 0,
                rawDate: d
            });
        }
        return {
            name: t("topics_chart.no_data"),
            history,
            total: 0,
            Icon: defaultIcon
        };
    }, [t, language]);

    const processedData = useMemo(() => {
        if (!rawData || rawData.length === 0) return [];

        let minTime = Infinity;
        let maxTime = -Infinity;

        const parsedTopics = rawData.map(topic => {
            const originalName = topic.name || 'Unknown';
            const displayName =
                language === 'es'
                    ? topic.topic_es || originalName
                    : language === 'ca'
                        ? topic.topic_ca || originalName
                        : originalName;

            let rawEntries: { time: number; value: number }[] = [];

            const entries = topic.topics_per_day;

            if (entries) {
                if (Array.isArray(entries)) {
                    rawEntries = entries.map(d => {
                        const dateObj = new Date(d.date);
                        dateObj.setHours(0, 0, 0, 0);
                        const time = dateObj.getTime();
                        if (time < minTime) minTime = time;
                        if (time > maxTime) maxTime = time;
                        return { time, value: d.docs_number || 0 };
                    });
                } else {
                    rawEntries = Object.entries(entries).map(([date, val]) => {
                        const dateObj = new Date(date);
                        dateObj.setHours(0, 0, 0, 0);
                        const time = dateObj.getTime();
                        if (time < minTime) minTime = time;
                        if (time > maxTime) maxTime = time;
                        return { time, value: Number(val) };
                    });
                }
            }

            return {
                name: displayName,
                rawEntries,
                Icon: iconMap[originalName] ?? defaultIcon
            };
        });

        if (minTime === Infinity || maxTime === -Infinity) return [];

        const allDaysInRange: Date[] = [];
        let currentIter = new Date(minTime);
        const endDate = new Date(maxTime);

        while (currentIter <= endDate) {
            allDaysInRange.push(new Date(currentIter));
            currentIter.setDate(currentIter.getDate() + 1);
        }

        const finalTopics = parsedTopics.map(topic => {
            const valueMap = new Map<number, number>();
            topic.rawEntries.forEach(e => valueMap.set(e.time, e.value));

            const fullHistory = allDaysInRange.map(dateObj => {
                const time = dateObj.getTime();
                let dateStr = dateObj.toLocaleDateString(language, { weekday: 'short', day: 'numeric' });
                dateStr = dateStr.charAt(0).toUpperCase() + dateStr.slice(1).replace(" de ", " ").replace(" del ", " ");
                return {
                    date: dateStr,
                    value: valueMap.get(time) || 0,
                    rawDate: dateObj
                };
            });

            const total = fullHistory.reduce((acc, curr) => acc + curr.value, 0);

            return {
                name: topic.name,
                history: fullHistory,
                total,
                Icon: topic.Icon
            };
        });

        return finalTopics
            .filter(t => t.total > 0)
            .sort((a, b) => b.total - a.total)
            .slice(0, TOP_N);
    }, [rawData, language, t]);

    const hasData = processedData.length > 0;
    const activeTopic = hasData ? (processedData[activeTab] || processedData[0]) : emptyTopic;

    return (
        <div className="w-full bg-card p-6 rounded-xl border border-border flex flex-col gap-8 shadow-sm h-full">

            <div className="flex flex-col gap-6">
                <div>
                    <h3 className="text-lg font-semibold text-foreground">{t("topics_chart.title", { count: TOP_N })}</h3>
                </div>

                {hasData && (
                    <div className="flex flex-wrap justify-center gap-3">
                        {processedData.map((topic, index) => (
                            <div key={topic.name} className="relative group">
                                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-[10px] font-bold rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-[100] shadow-xl">
                                    {topic.name.toUpperCase()}
                                    <div className="absolute top-full left-1/2 -translate-x-1/2 border-[4px] border-transparent border-t-gray-900" />
                                </div>

                                <button
                                    onClick={() => setActiveTab(index)}
                                    className={`flex items-center justify-center w-12 h-12 rounded-lg transition-all duration-200 border-2 ${activeTab === index
                                        ? 'bg-[#f7c873] text-[#1a2238] border-[#f7c873] shadow-md scale-105'
                                        : 'bg-[#f7c873]/20 text-[#1a2238] border-transparent hover:bg-[#f7c873]/40'
                                        }`}
                                >
                                    <topic.Icon className="w-6 h-6" />
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="flex-1 w-full min-h-[200px] flex flex-col">
                <div className="mb-6 flex items-center gap-3">
                    <div className="w-2 h-8 rounded-full bg-[#f7c873]" />
                    <div className="flex flex-col">
                        <span className="text-sm font-bold text-foreground uppercase tracking-tight leading-none">
                            {activeTopic.name}
                        </span>
                        <span className="text-xs text-muted-foreground mt-1">
                            {activeTopic.total} {t("topics_chart.total_news")}
                        </span>
                    </div>
                </div>

                <div className="flex-1 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={activeTopic.history} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} strokeOpacity={0.1} />
                            <XAxis
                                dataKey="date"
                                axisLine={false}
                                tickLine={false}
                                tick={{ fontSize: 10, fill: '#64748b', fontWeight: 500 }}
                                interval={0}
                                angle={-45}
                                textAnchor="end"
                                height={60}
                            />
                            <YAxis
                                axisLine={false}
                                tickLine={false}
                                tick={{ fontSize: 11, fill: '#64748b', fontWeight: 500 }}
                            />
                            <Tooltip
                                cursor={false}
                                formatter={(value: number | undefined) => [value ?? 0, t("topics_chart.docs")]}
                                contentStyle={{
                                    borderRadius: '12px',
                                    border: 'none',
                                    boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)',
                                    fontSize: '12px',
                                    fontWeight: '600'
                                }}
                            />
                            <Bar
                                dataKey="value"
                                radius={[4, 4, 0, 0]}
                                animationDuration={1000}
                            >
                                {activeTopic.history.map((entry, index) => (
                                    <Cell
                                        key={`cell-${index}`}
                                        fill={PRIMARY_YELLOW}
                                    />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

export default TopicsChart;