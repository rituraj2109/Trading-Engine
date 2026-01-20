import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Activity, RefreshCw, Newspaper, TrendingUp, X } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import API_URL from './config';


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

    // Chart State
    const [selectedPair, setSelectedPair] = useState(null);
    const [chartData, setChartData] = useState([]);
    const [chartLoading, setChartLoading] = useState(false);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [signalsRes, newsRes, statusRes] = await Promise.all([
                axios.get(`${API_URL}/api/signals`),
                axios.get(`${API_URL}/api/news`),
                axios.get(`${API_URL}/api/status`).catch(() => ({ data: { status: 'offline' } }))
            ]);
            setSignals(signalsRes.data || []);
            setNews(newsRes.data || []);
            setStatus(statusRes.data);
        } catch (error) {
            console.error("Error fetching data:", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchChartData = async (pair) => {
        setChartLoading(true);
        setSelectedPair(pair);
        try {
            // Get last 100 data points (15 min candles)
            const res = await axios.get(`${API_URL}/api/data/${pair}?limit=100`);
            setChartData(res.data);
        } catch (err) {
            console.error("Chart fetch error", err);
        } finally {
            setChartLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 15000); // Poll every 15s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="min-h-screen bg-slate-900 text-slate-100 font-sans selection:bg-blue-500/30">
            {/* Header */}
            <header className="fixed top-0 w-full z-50 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-900/20">
                        <Activity className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                            Forex AI Engine
                        </h1>
                        <p className="text-xs text-slate-400 font-medium tracking-wide flex items-center gap-2">
                            Status:
                            <span className={status.status === 'running' ? 'text-emerald-400' : 'text-red-400'}>
                                {status.status && status.status.toUpperCase()}
                            </span>
                            |
                            DB:
                            <span className={status.mongodb === 'connected' ? 'text-emerald-400' : 'text-red-400'}>
                                {status.mongodb === 'connected' ? 'MONGO' : 'ERROR'}
                            </span>
                        </p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={async () => {
                            setLoading(true);
                            await axios.post(`${API_URL}/api/scan`);
                            setTimeout(fetchData, 4000);
                        }}
                        className="px-4 py-2 bg-blue-600 rounded-lg hover:bg-blue-500 transition-colors text-sm font-semibold flex items-center gap-2"
                    >
                        <Activity className="w-4 h-4" />
                        Scan Now
                    </button>
                    <button
                        onClick={fetchData}
                        className="p-2 bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors border border-slate-700 hover:border-blue-500"
                    >
                        <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </header>

            <main className="max-w-7xl mx-auto pt-24 pb-10 px-6 grid grid-cols-1 lg:grid-cols-3 gap-8">

                {/* Signals Column */}
                <div className="lg:col-span-2 space-y-6">
                    <h2 className="text-2xl font-bold flex items-center gap-2">
                        <TrendingUp className="w-6 h-6 text-blue-400" />
                        Live Signals
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {signals.map((signal, idx) => {
                            const isBuy = signal.signal === 'BUY';
                            const isSell = signal.signal === 'SELL';
                            const isWait = signal.signal === 'WAIT';

                            let shadowColor = 'shadow-slate-900/20';
                            let borderColor = 'border-slate-800';
                            let signalColor = 'text-slate-400';
                            let bgGradient = 'from-slate-800 to-slate-900';

                            if (isBuy) {
                                shadowColor = 'shadow-emerald-900/20';
                                borderColor = 'border-emerald-500/30';
                                signalColor = 'text-emerald-400';
                                bgGradient = 'from-emerald-900/10 to-slate-900';
                            } else if (isSell) {
                                shadowColor = 'shadow-rose-900/20';
                                borderColor = 'border-rose-500/30';
                                signalColor = 'text-rose-400';
                                bgGradient = 'from-rose-900/10 to-slate-900';
                            }

                            return (
                                <div
                                    key={idx}
                                    className={`relative group bg-gradient-to-br ${bgGradient} border ${borderColor} rounded-2xl p-6 shadow-xl ${shadowColor} hover:scale-[1.02] transition-all duration-300 cursor-pointer`}
                                    onClick={() => fetchChartData(signal.pair)}
                                >
                                    <div className="flex justify-between items-start mb-4">
                                        <div>
                                            <h3 className="text-2xl font-bold tracking-tight">{signal.pair}</h3>
                                            <p className="text-xs text-slate-500 font-mono mt-1">{formatTime(signal.time)}</p>
                                        </div>
                                        <div className={`px-3 py-1 rounded-full text-xs font-bold border ${borderColor} bg-slate-900/50 backdrop-blur-sm ${signalColor}`}>
                                            {signal.signal}
                                        </div>
                                    </div>

                                    <div className="flex items-end justify-between mb-4">
                                        <div>
                                            <p className="text-slate-500 text-xs uppercase font-semibold mb-1">Entry Price</p>
                                            <p className="text-3xl font-bold tabular-nums tracking-tight">
                                                {signal.entry_price}
                                            </p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-slate-500 text-xs uppercase font-semibold mb-1">Confidence</p>
                                            <p className={`text-xl font-bold tabular-nums ${signal.confidence > 70 ? 'text-blue-400' : 'text-slate-400'}`}>
                                                {signal.confidence}%
                                            </p>
                                        </div>
                                    </div>

                                    {!isWait && (
                                        <div className="grid grid-cols-2 gap-3 mb-4 p-3 bg-slate-900/50 rounded-xl border border-slate-800/50">
                                            <div>
                                                <p className="text-[10px] text-slate-500 uppercase font-bold">Stop Loss</p>
                                                <p className="text-sm font-semibold text-rose-300 tabular-nums">{signal.stop_loss}</p>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-[10px] text-slate-500 uppercase font-bold">Take Profit</p>
                                                <p className="text-sm font-semibold text-emerald-300 tabular-nums">{signal.take_profit}</p>
                                            </div>
                                        </div>
                                    )}

                                    <div className="relative pt-3 border-t border-slate-800/50">
                                        <p className="text-sm text-slate-400 line-clamp-2 leading-relaxed">
                                            {signal.reason}
                                        </p>
                                        <div className="absolute top-0 right-0 -mt-2 p-1 bg-slate-800 rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
                                            <TrendingUp className="w-3 h-3 text-blue-400" />
                                        </div>
                                    </div>

                                    <div className="mt-2 text-center">
                                        <span className="text-xs text-blue-400 font-medium group-hover:text-blue-300 transition-colors">Click to View Chart</span>
                                    </div>
                                </div>
                            );
                        })}
                        {signals.length === 0 && !loading && (
                            <div className="col-span-full text-center py-10 text-slate-500 bg-slate-800/20 rounded-2xl border border-slate-800 border-dashed">
                                Start the engine or click Scan Now to generate signals.
                            </div>
                        )}
                    </div>
                </div>

                {/* News Column */}
                <div className="space-y-6">
                    <h2 className="text-2xl font-bold flex items-center gap-2">
                        <Newspaper className="w-6 h-6 text-purple-400" />
                        Market News
                    </h2>
                    <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-4 h-[calc(100vh-12rem)] overflow-y-auto custom-scrollbar">
                        <div className="space-y-4">
                            {news.map((item, idx) => (
                                <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-4 hover:border-slate-700 transition-colors">
                                    <div className="flex justify-between items-start gap-3 mb-2">
                                        <h4 className="font-semibold text-sm leading-snug line-clamp-2">
                                            {item.title}
                                        </h4>
                                        <span className={`shrink-0 w-2 h-2 rounded-full mt-1.5 ${item.sentiment_score > 0 ? 'bg-emerald-500' : item.sentiment_score < 0 ? 'bg-rose-500' : 'bg-slate-500'}`} />
                                    </div>
                                    <div className="flex justify-between items-center text-xs text-slate-500">
                                        <span className="font-medium text-slate-400">{item.source}</span>
                                        <span>{new Date(item.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </main>

            {/* Chart Modal */}
            {selectedPair && (
                <div className="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
                    <div className="bg-slate-900 border border-slate-700 w-full max-w-4xl rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
                        <div className="flex items-center justify-between p-4 border-b border-slate-800">
                            <h3 className="text-xl font-bold flex items-center gap-2">
                                {selectedPair} <span className="text-slate-500 text-sm font-normal">Price History (Last 100 Candles - 15m)</span>
                            </h3>
                            <button
                                onClick={() => setSelectedPair(null)}
                                className="p-2 hover:bg-slate-800 rounded-lg transition-colors text-slate-400 hover:text-white"
                            >
                                <X className="w-6 h-6" />
                            </button>
                        </div>
                        <div className="p-6 h-[400px]">
                            {chartLoading ? (
                                <div className="h-full flex items-center justify-center">
                                    <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
                                </div>
                            ) : chartData.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={chartData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                        <XAxis
                                            dataKey="time"
                                            tickFormatter={(t) => new Date(t).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            stroke="#64748b"
                                            tick={{ fontSize: 12 }}
                                            minTickGap={30}
                                        />
                                        <YAxis
                                            domain={['auto', 'auto']}
                                            stroke="#64748b"
                                            tick={{ fontSize: 12 }}
                                        />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f1f5f9' }}
                                            itemStyle={{ color: '#3b82f6' }}
                                            labelStyle={{ color: '#94a3b8' }}
                                            labelFormatter={(l) => new Date(l).toLocaleString()}
                                        />
                                        <Line
                                            type="monotone"
                                            dataKey="close"
                                            stroke="#3b82f6"
                                            strokeWidth={2}
                                            dot={false}
                                            activeDot={{ r: 6 }}
                                            animationDuration={1000}
                                        />
                                    </LineChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="h-full flex flex-col items-center justify-center text-slate-500">
                                    <Activity className="w-12 h-12 mb-2 opacity-50" />
                                    <p>No historical data available for this chart yet.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default App;
