import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Activity, ArrowUp, ArrowDown, Minus, RefreshCw, Newspaper, TrendingUp } from 'lucide-react';

// Utils
const formatTime = (timeStr) => {
    if (!timeStr) return '';
    return new Date(timeStr).toLocaleString();
};

function App() {
    const [signals, setSignals] = useState([]);
    const [news, setNews] = useState([]);
    const [status, setStatus] = useState({ status: 'connecting...' });
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [signalsRes, newsRes, statusRes] = await Promise.all([
                axios.get('/api/signals'),
                axios.get('/api/news'),
                axios.get('/api/status').catch(() => ({ data: { status: 'offline' } }))
            ]);

            setSignals(signalsRes.data || []);
            setNews(newsRes.data || []);
            setStatus(statusRes.data);
        } catch (error) {
            console.error("Error fetching data", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="min-h-screen bg-slate-900 text-slate-100 p-6 font-sans">
            {/* Header */}
            <header className="max-w-7xl mx-auto mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
                        Forex Engine Dashboard
                    </h1>
                    <p className="text-slate-400 mt-1 flex items-center gap-2">
                        Status: <span className={`w-2 h-2 rounded-full ${status.status === 'running' ? 'bg-green-500' : 'bg-red-500'}`}></span>
                        {status.status}
                    </p>
                </div>
                <button
                    onClick={fetchData}
                    className="p-2 bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors border border-slate-700 hover:border-blue-500"
                >
                    <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                </button>
            </header>

            <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">

                {/* Signals Column (Left - Wider) */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="flex items-center gap-2 mb-4">
                        <Activity className="text-blue-400" />
                        <h2 className="text-xl font-semibold">Live Signals</h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {signals.map((signal) => (
                            <SignalCard key={`${signal.pair}-${signal.time}`} signal={signal} />
                        ))}
                        {signals.length === 0 && !loading && (
                            <p className="text-slate-500 italic">No signals generated yet or engine is starting up...</p>
                        )}
                    </div>
                </div>

                {/* News Column (Right) */}
                <div className="space-y-6">
                    <div className="flex items-center gap-2 mb-4">
                        <Newspaper className="text-purple-400" />
                        <h2 className="text-xl font-semibold">Latest News</h2>
                    </div>

                    <div className="space-y-4 max-h-[800px] overflow-y-auto pr-2 custom-scrollbar">
                        {news.map((item) => (
                            <NewsCard key={item.id} item={item} />
                        ))}
                        {news.length === 0 && !loading && (
                            <p className="text-slate-500 italic">No news found.</p>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}

// Components
const SignalCard = ({ signal }) => {
    const isBuy = signal.signal === 'BUY';
    const isSell = signal.signal === 'SELL';
    const isWait = signal.signal === 'WAIT';

    let borderColor = 'border-slate-700';
    let badgeColor = 'bg-slate-700 text-slate-300';
    let priceColor = 'text-slate-100';

    if (isBuy) {
        borderColor = 'border-green-500/50 shadow-[0_0_15px_-3px_rgba(34,197,94,0.2)]';
        badgeColor = 'bg-green-500/20 text-green-400 border border-green-500/30';
        priceColor = 'text-green-400';
    } else if (isSell) {
        borderColor = 'border-red-500/50 shadow-[0_0_15px_-3px_rgba(239,68,68,0.2)]';
        badgeColor = 'bg-red-500/20 text-red-400 border border-red-500/30';
        priceColor = 'text-red-400';
    }

    return (
        <div className={`bg-slate-800/50 rounded-xl p-5 border ${borderColor} backdrop-blur-sm transition-all hover:scale-[1.01]`}>
            <div className="flex justify-between items-start mb-3">
                <div>
                    <h3 className="text-2xl font-bold tracking-tight">{signal.pair}</h3>
                    <p className="text-xs text-slate-400">{formatTime(signal.time)}</p>
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-bold flex items-center gap-1 ${badgeColor}`}>
                    {isBuy && <ArrowUp className="w-4 h-4" />}
                    {isSell && <ArrowDown className="w-4 h-4" />}
                    {isWait && <Minus className="w-4 h-4" />}
                    {signal.signal}
                </div>
            </div>

            <div className="space-y-3">
                <div className="flex justify-between items-baseline">
                    <span className="text-slate-400 text-sm">Price</span>
                    <span className={`text-lg font-mono font-medium ${priceColor}`}>{signal.entry_price}</span>
                </div>

                {!isWait && (
                    <>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                            <div className="bg-slate-900/50 p-2 rounded">
                                <span className="text-slate-500 block text-xs">TP</span>
                                <span className="text-green-300 font-mono">{signal.take_profit}</span>
                            </div>
                            <div className="bg-slate-900/50 p-2 rounded">
                                <span className="text-slate-500 block text-xs">SL</span>
                                <span className="text-red-300 font-mono">{signal.stop_loss}</span>
                            </div>
                        </div>
                        <div className="pt-2 border-t border-slate-700/50">
                            <span className="text-slate-400 text-xs">Confidence</span>
                            <div className="w-full bg-slate-700 h-1.5 rounded-full mt-1 overflow-hidden">
                                <div
                                    className="bg-blue-500 h-full rounded-full"
                                    style={{ width: `${signal.confidence}%` }}
                                ></div>
                            </div>
                        </div>
                    </>
                )}

                <div className="bg-slate-900/30 p-2 rounded border border-slate-700/30">
                    <p className="text-xs text-slate-300 leading-relaxed line-clamp-2" title={signal.reason}>
                        {signal.reason}
                    </p>
                </div>
            </div>
        </div>
    );
};

const NewsCard = ({ item }) => (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 hover:border-slate-600 transition-colors">
        <div className="flex justify-between items-start mb-2">
            <span className="text-xs text-blue-400 font-medium px-2 py-0.5 bg-blue-400/10 rounded border border-blue-400/20">
                {item.source}
            </span>
            <span className="text-xs text-slate-500">{new Date(item.date).toLocaleDateString()}</span>
        </div>
        <h4 className="text-sm font-medium text-slate-200 mb-2 line-clamp-2 hover:text-blue-300 transition-colors">
            {item.title}
        </h4>
        <p className="text-xs text-slate-400 line-clamp-3">
            {item.sentiment_score !== 0 && (
                <span className={`mr-2 ${item.sentiment_score > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {item.sentiment_score > 0 ? 'bullish' : 'bearish'}
                </span>
            )}
        </p>
    </div>
);

export default App;
