import { Fragment, useMemo, useState } from 'react';
import type { Risk, Finding } from '../types';
import { AlertTriangle, ExternalLink } from 'lucide-react';

interface RiskMatrixProps {
    risks: Risk[];
    findings: Finding[];
}

export function RiskMatrix({ risks, findings }: RiskMatrixProps) {
    const severityLevels = ['low', 'medium', 'high'];
    const likelihoodLevels = ['low', 'medium', 'high'];
    const [compact, setCompact] = useCompactContext();

    const getCell = (severity: string, likelihood: string) => {
        return risks.filter(r => r.severity === severity && r.likelihood === likelihood);
    };

    const getCellPalette = (severity: string, likelihood: string) => {
        // 5-step palette across 9 cells (sum index 0..4)
        const score = severityLevels.indexOf(severity) + likelihoodLevels.indexOf(likelihood);
        switch (score) {
            case 0:
                return { bg: 'bg-emerald-600/40', bgEmpty: 'bg-emerald-600/10', hover: 'hover:bg-emerald-600/60', border: 'border-emerald-600', ring: 'hover:ring-emerald-400/50' };
            case 1:
                return { bg: 'bg-lime-600/40', bgEmpty: 'bg-lime-600/10', hover: 'hover:bg-lime-600/60', border: 'border-lime-600', ring: 'hover:ring-lime-400/50' };
            case 2:
                return { bg: 'bg-yellow-600/40', bgEmpty: 'bg-yellow-600/10', hover: 'hover:bg-yellow-600/60', border: 'border-yellow-600', ring: 'hover:ring-yellow-400/50' };
            case 3:
                return { bg: 'bg-orange-600/40', bgEmpty: 'bg-orange-600/10', hover: 'hover:bg-orange-600/60', border: 'border-orange-600', ring: 'hover:ring-orange-400/50' };
            default:
                return { bg: 'bg-red-600/40', bgEmpty: 'bg-red-600/10', hover: 'hover:bg-red-600/60', border: 'border-red-600', ring: 'hover:ring-red-400/50' };
        }
    };

    const slugify = (text: string) =>
        text
            .toLowerCase()
            .replace(/\s+/g, '-')
            .replace(/[^a-z0-9\-]/g, '');

    // Pre-sort findings by relevance
    const orderedFindings = useMemo(() => [...findings].sort((a, b) => b.page_relevance - a.page_relevance), [findings]);

    const pickSourceForRisk = (risk: Risk): string | null => {
        const titleLc = risk.risk.toLowerCase();
        const significantWords = risk.risk
            .split(/[^A-Za-z0-9ÄÖÜäöüß]+/)
            .filter(w => w.length > 4)
            .map(w => w.toLowerCase());
        for (const f of orderedFindings) {
            if (f.key_findings.some(kf => kf.toLowerCase().includes(titleLc))) return f.url;
            if (f.key_findings.some(kf => significantWords.some(sw => kf.toLowerCase().includes(sw)))) return f.url;
        }
        return orderedFindings[0]?.url || null;
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between flex-wrap gap-3">
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                    <AlertTriangle className="w-6 h-6" />
                    Risk Matrix
                </h2>
                <div className="flex items-center gap-2">
                    <CompactToggle onToggle={() => setCompact(!compact)} compact={compact} />
                    <ExportPdfButton />
                </div>
            </div>

            {/* Legend */}
            <div className="flex flex-wrap items-center gap-3 text-sm text-slate-300">
                <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-sm bg-emerald-600/60 border border-emerald-600/70"></span>
                    Very Low
                </div>
                <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-sm bg-lime-600/60 border border-lime-600/70"></span>
                    Low
                </div>
                <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-sm bg-yellow-600/60 border border-yellow-600/70"></span>
                    Medium
                </div>
                <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-sm bg-orange-600/60 border border-orange-600/70"></span>
                    High
                </div>
                <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-sm bg-red-600/60 border border-red-600/70"></span>
                    Very High
                </div>
                <div className="opacity-60">•</div>
                <div className="flex items-center gap-1">
                    <span className="font-semibold text-slate-200">Rows:</span>
                    Severity low → high
                </div>
                <div className="flex items-center gap-1">
                    <span className="font-semibold text-slate-200">Columns:</span>
                    Likelihood low → high
                </div>
            </div>

            {/* Matrix Grid */}
            <div className="overflow-x-auto">
                <div className="inline-grid grid-cols-4 gap-2 min-w-[700px]">
                    {/* Header Row */}
                    <div></div>
                    {likelihoodLevels.map(l => (
                        <div key={l} className="text-center font-semibold text-white py-2">
                            Likelihood: {l.toUpperCase()}
                        </div>
                    ))}

                    {/* Data Rows */}
                    {[...severityLevels].reverse().map(severity => (
                        <Fragment key={severity}>
                            <div className="flex items-center justify-end pr-4 font-semibold text-white">
                                Severity: {severity.toUpperCase()}
                            </div>
                            {likelihoodLevels.map(likelihood => {
                                const cellRisks = getCell(severity, likelihood);
                                const palette = getCellPalette(severity, likelihood);
                                const firstTargetId = cellRisks.length > 0 ? `risk-${slugify(cellRisks[0].risk)}` : undefined;

                                return (
                                    <div
                                        key={`${severity}-${likelihood}`}
                                        className={`${cellRisks.length > 0 ? palette.bg : palette.bgEmpty} border-2 ${palette.border} rounded-lg ${compact ? 'p-2 min-h-[80px]' : 'p-3 min-h-[120px]'} ${palette.hover} ${palette.ring} hover:ring-2 transition-colors relative`}
                                        title={`${cellRisks.length} risk${cellRisks.length === 1 ? '' : 's'} in ${severity.toUpperCase()} severity / ${likelihood.toUpperCase()} likelihood`}
                                    >
                                        {cellRisks.length > 0 && (
                                            <>
                                                {/* Count badge */}
                                                <button
                                                    type="button"
                                                    className="absolute top-2 right-2 text-[11px] px-2 py-0.5 rounded-full bg-slate-900/70 text-slate-200 border border-white/10 hover:bg-slate-800/90"
                                                    onClick={() => {
                                                        if (!firstTargetId) return;
                                                        document.getElementById(firstTargetId)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                                                    }}
                                                >
                                                    {cellRisks.length}
                                                </button>

                                                <div className={`${compact ? 'space-y-1' : 'space-y-2'}`}>
                                                    {cellRisks.map((risk, idx) => {
                                                        const sourceUrl = pickSourceForRisk(risk);
                                                        const targetId = `risk-${slugify(risk.risk)}`;
                                                        return (
                                                            <button
                                                                key={idx}
                                                                type="button"
                                                                onClick={() => document.getElementById(targetId)?.scrollIntoView({ behavior: 'smooth', block: 'start' })}
                                                                className={`w-full text-left bg-slate-800/80 rounded ${compact ? 'p-1' : 'p-2'} text-xs hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-offset-0 focus:ring-slate-600/60`}
                                                            >
                                                                <div className={`font-medium text-white ${compact ? 'mb-0.5' : 'mb-1'} line-clamp-2`}>{risk.risk}</div>
                                                                <div className="flex items-center justify-between text-slate-400 gap-2">
                                                                    <span className="px-1.5 py-0.5 bg-blue-500/20 text-blue-300 rounded">
                                                                        {risk.area}
                                                                    </span>
                                                                    {sourceUrl && (
                                                                        <a
                                                                            href={sourceUrl}
                                                                            target="_blank"
                                                                            rel="noopener noreferrer"
                                                                            className="inline-flex items-center gap-1 text-blue-400 hover:text-blue-300"
                                                                            onClick={(e) => e.stopPropagation()}
                                                                            title="Open source"
                                                                        >
                                                                            <ExternalLink className="w-3 h-3" />
                                                                        </a>
                                                                    )}
                                                                </div>
                                                            </button>
                                                        );
                                                    })}
                                                </div>
                                            </>
                                        )}
                                    </div>
                                );
                            })}
                        </Fragment>
                    ))}
                </div>
            </div>

            {/* Risk Details */}
            <div className="mt-6 space-y-3">
                <h3 className="text-xl font-semibold text-white">Risk Details</h3>
                {risks.map((risk, idx) => {
                    const sourceUrl = pickSourceForRisk(risk);
                    return (
                        <div key={idx} id={`risk-${slugify(risk.risk)}`} className={`bg-slate-800 rounded-lg ${compact ? 'p-3' : 'p-4'}`}>
                            <div className="flex items-start justify-between mb-2">
                                <h4 className="font-semibold text-white">{risk.risk}</h4>
                                <div className="flex gap-2">
                                    <span className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs">{risk.area}</span>
                                    <span className={`px-2 py-1 rounded text-xs ${risk.severity === 'high' ? 'bg-red-500/20 text-red-300' :
                                        risk.severity === 'medium' ? 'bg-yellow-500/20 text-yellow-300' :
                                            'bg-green-500/20 text-green-300'
                                        }`}>
                                        Severity: {risk.severity}
                                    </span>
                                    {sourceUrl && (
                                        <a
                                            href={sourceUrl}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="inline-flex items-center gap-1 text-blue-400 hover:text-blue-300 text-xs"
                                            title="Open source"
                                        >
                                            <ExternalLink className="w-3 h-3" /> Source
                                        </a>
                                    )}
                                </div>
                            </div>
                            <div className={`grid md:grid-cols-3 ${compact ? 'gap-2 text-[13px]' : 'gap-3 text-sm'} text-slate-300`}>
                                <div>
                                    <span className="font-medium text-slate-400">Consequence:</span>
                                    <p>{risk.consequence}</p>
                                </div>
                                <div>
                                    <span className="font-medium text-slate-400">Mitigation:</span>
                                    <p>{risk.mitigation}</p>
                                </div>
                                <div>
                                    <span className="font-medium text-slate-400">Detection:</span>
                                    <p>{risk.detection}</p>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

// Local UI controls
function CompactToggle({ compact, onToggle }: { compact: boolean; onToggle: () => void }) {
    return (
        <button
            type="button"
            onClick={onToggle}
            className={`inline-flex items-center gap-2 px-3 py-1.5 rounded border border-slate-600 ${compact ? 'bg-slate-700 text-slate-200' : 'bg-slate-800 text-slate-300'} hover:bg-slate-700`}
            title="Compact view"
        >
            <span className="text-xs">{compact ? 'Compact: ON' : 'Compact: OFF'}</span>
        </button>
    );
}

function ExportPdfButton() {
    const onExport = async () => {
        // Lightweight fallback: use browser print to allow Save as PDF
        window.print();
    };
    return (
        <button
            type="button"
            onClick={onExport}
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded border border-slate-600 bg-slate-800 text-slate-300 hover:bg-slate-700"
            title="Export as PDF"
        >
            <span className="text-xs">Export PDF</span>
        </button>
    );
}

// Simple compact view context using module-level signal
let compactState = false;
const listeners = new Set<(v: boolean) => void>();
function useCompactContext(): [boolean, (v: boolean) => void] {
    const [value, setValue] = useState(compactState);
    const set = (v: boolean) => {
        compactState = v;
        setValue(v);
        listeners.forEach(fn => fn(v));
    };
    // sync across instances
    useMemo(() => {
        const fn = (v: boolean) => setValue(v);
        listeners.add(fn);
        return () => listeners.delete(fn);
    }, []);
    return [value, set];
}
