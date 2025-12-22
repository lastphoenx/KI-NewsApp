import type { Action } from '../types';
import { CheckCircle2, Clock, User } from 'lucide-react';
import { format, parseISO } from 'date-fns';

interface ActionBoardProps {
    actions: Action[];
}

export function ActionBoard({ actions }: ActionBoardProps) {
    const grouped = {
        high: actions.filter(a => a.priority === 'high'),
        medium: actions.filter(a => a.priority === 'medium'),
        low: actions.filter(a => a.priority === 'low'),
    };

    const Column = ({ title, items, color }: { title: string; items: Action[]; color: string }) => (
        <div className="flex-1 min-w-[300px]">
            <div className={`${color} text-white px-4 py-2 rounded-t-lg font-semibold flex items-center gap-2`}>
                <CheckCircle2 className="w-5 h-5" />
                {title}
                <span className="ml-auto bg-white/20 px-2 py-0.5 rounded-full text-sm">{items.length}</span>
            </div>
            <div className="bg-slate-800/50 p-3 rounded-b-lg space-y-3 min-h-[400px]">
                {items.map((action, idx) => (
                    <div key={idx} className="bg-slate-800 rounded-lg p-4 shadow-md hover:shadow-lg transition-shadow">
                        <h4 className="font-medium text-white mb-2">{action.action}</h4>

                        <div className="space-y-2 text-sm">
                            <div className="flex items-center gap-2 text-slate-300">
                                <Clock className="w-4 h-4" />
                                <span className="font-medium">Deadline:</span>
                                <span>{format(parseISO(action.deadline), 'dd.MM.yyyy')}</span>
                            </div>

                            <div className="flex items-center gap-2 text-slate-300">
                                <User className="w-4 h-4" />
                                <span className="font-medium">Owner:</span>
                                <span>{action.owner_role}</span>
                            </div>

                            <div className="flex items-center gap-2 text-slate-300">
                                <span className="font-medium">Effort:</span>
                                <span className="px-2 py-0.5 bg-purple-500/20 text-purple-300 rounded">
                                    {action.effort}
                                </span>
                            </div>
                        </div>

                        <p className="text-xs text-slate-400 mt-3 italic">{action.reason}</p>
                    </div>
                ))}
            </div>
        </div>
    );

    return (
        <div className="space-y-4">
            <h2 className="text-2xl font-bold text-white">Action Board (Kanban)</h2>
            <div className="flex gap-4 overflow-x-auto pb-4">
                <Column title="🔴 HIGH Priority" items={grouped.high} color="bg-red-600" />
                <Column title="🟡 MEDIUM Priority" items={grouped.medium} color="bg-yellow-600" />
                <Column title="🟢 LOW Priority" items={grouped.low} color="bg-green-600" />
            </div>
        </div>
    );
}
