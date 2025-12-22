import type { Change, Finding } from '../types';
import { format, parseISO } from 'date-fns';
import { Calendar, ExternalLink } from 'lucide-react';

interface TimelineProps {
    changes: Change[];
    findings: Finding[];
}

// Removed stray Python-style helper; using pickSourceFor below.

export function Timeline({ changes, findings }: TimelineProps) {
    const sorted = [...changes].sort(
        (a, b) => new Date(a.effective_date).getTime() - new Date(b.effective_date).getTime()
    );

    // Pre-sort findings by relevance once
    const orderedFindings = [...findings].sort(
        (a, b) => b.page_relevance - a.page_relevance
    );

    const pickSourceFor = (change: Change): string | null => {
        // Direct URL in spec_reference?
        if (/^https?:\/\//i.test(change.spec_reference)) return change.spec_reference;
        const topicLc = change.topic.toLowerCase();
        const significantWords = change.description
            .split(/[^A-Za-z0-9ÄÖÜäöüß]+/)
            .filter(w => w.length > 4)
            .map(w => w.toLowerCase());
        for (const f of orderedFindings) {
            // Check key findings text for topic or significant words
            if (f.key_findings.some(kf => kf.toLowerCase().includes(topicLc))) {
                return f.url;
            }
            if (f.key_findings.some(kf => significantWords.some(sw => kf.toLowerCase().includes(sw)))) {
                return f.url;
            }
        }
        // Fallback: highest relevance page
        return orderedFindings[0]?.url || null;
    };

    const getImpactColor = (impact: string) => {
        switch (impact) {
            case 'high': return 'bg-red-500';
            case 'medium': return 'bg-yellow-500';
            case 'low': return 'bg-green-500';
            default: return 'bg-gray-500';
        }
    };

    return (
        <div className="space-y-4">
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                <Calendar className="w-6 h-6" />
                Timeline - Deadlines & Changes
            </h2>

            <div className="relative pl-8 space-y-6">
                {/* Vertical Line */}
                <div className="absolute left-2 top-0 bottom-0 w-0.5 bg-slate-700"></div>

                {sorted.map((change, idx) => {
                    const sourceUrl = pickSourceFor(change);
                    return (
                        <div key={idx} className="relative">
                            {/* Dot */}
                            <div className={`absolute left-[-1.75rem] w-4 h-4 rounded-full ${getImpactColor(change.impact)} border-4 border-slate-900`}></div>

                            {/* Card */}
                            <div className="bg-slate-800 rounded-lg p-4 shadow-lg">
                                <div className="flex items-start justify-between mb-2">
                                    <div>
                                        <span className="text-xs text-slate-400">
                                            {format(parseISO(change.effective_date), 'dd. MMM yyyy')}
                                        </span>
                                        <h3 className="text-lg font-semibold text-white">{change.topic}</h3>
                                    </div>
                                    <span className={`px-2 py-1 rounded text-xs font-medium ${change.impact === 'high' ? 'bg-red-500/20 text-red-300' :
                                        change.impact === 'medium' ? 'bg-yellow-500/20 text-yellow-300' :
                                            'bg-green-500/20 text-green-300'
                                        }`}>
                                        {change.impact.toUpperCase()}
                                    </span>
                                </div>

                                <p className="text-slate-300 text-sm mb-3">{change.description}</p>

                                <div className="flex flex-wrap gap-2 mb-2">
                                    {change.affected_interfaces.map((iface, i) => (
                                        <span key={i} className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs">
                                            {iface}
                                        </span>
                                    ))}
                                </div>

                                <div className="flex items-center justify-between mt-2 text-xs text-slate-400">
                                    <div>
                                        <span className="font-medium">Spec:</span> {change.spec_reference}
                                    </div>
                                    {sourceUrl && (
                                        <a
                                            href={sourceUrl}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="inline-flex items-center gap-1 text-blue-400 hover:text-blue-300"
                                        >
                                            <ExternalLink className="w-3 h-3" /> Source
                                        </a>
                                    )}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
