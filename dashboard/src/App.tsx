import { useState, useEffect } from 'react';
import { api } from './api';
import type { Run } from './types';
import { Timeline } from './components/Timeline';
import { ActionBoard } from './components/ActionBoard';
import { RiskMatrix } from './components/RiskMatrix';
import { BarChart3, Loader2 } from 'lucide-react';

function App() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [selectedRun, setSelectedRun] = useState<Run | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'timeline' | 'actions' | 'risks'>('timeline');

  useEffect(() => {
    loadRuns();
  }, []);

  const loadRuns = async () => {
    try {
      const data = await api.getRuns();
      setRuns(data);
      if (data.length > 0) {
        setSelectedRun(data[0]);
      }
    } catch (error) {
      console.error('Failed to load runs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRunChange = async (runId: number) => {
    try {
      const run = await api.getRun(runId);
      setSelectedRun(run);
    } catch (error) {
      console.error('Failed to load run:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-slate-300">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!selectedRun) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center text-slate-300">
          <p className="text-xl">No runs available</p>
          <p className="text-sm mt-2">Start an analysis in the admin panel first</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-blue-500" />
            <div>
              <h1 className="text-2xl font-bold">NewsApp Dashboard</h1>
              <p className="text-sm text-slate-400">Analysis Results & Insights</p>
            </div>
          </div>

          <select
            value={selectedRun.id}
            onChange={(e) => handleRunChange(Number(e.target.value))}
            className="bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white"
          >
            {runs.map(run => (
              <option key={run.id} value={run.id}>
                Run #{run.id} - {run.summary?.ai_model || 'N/A'} ({run.created_at ? new Date(run.created_at).toLocaleDateString() : 'N/A'})
              </option>
            ))}
          </select>
        </div>
      </header>

      <div className="bg-slate-800/50 border-b border-slate-700 px-6 py-4">
        <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-800 rounded-lg p-3">
            <div className="text-slate-400 text-sm">Pages Analyzed</div>
            <div className="text-2xl font-bold">{selectedRun.summary?.pages_analyzed || 0}</div>
          </div>
          <div className="bg-slate-800 rounded-lg p-3">
            <div className="text-slate-400 text-sm">Avg. Score</div>
            <div className="text-2xl font-bold">{selectedRun.summary?.avg_page_score?.toFixed(1) || '0.0'}</div>
          </div>
          <div className="bg-slate-800 rounded-lg p-3">
            <div className="text-slate-400 text-sm">Changes Found</div>
            <div className="text-2xl font-bold">{selectedRun.changes?.length || 0}</div>
          </div>
          <div className="bg-slate-800 rounded-lg p-3">
            <div className="text-slate-400 text-sm">Actions Required</div>
            <div className="text-2xl font-bold">{selectedRun.actions?.length || 0}</div>
          </div>
        </div>
      </div>

      <div className="border-b border-slate-700 px-6">
        <div className="max-w-7xl mx-auto flex gap-4">
          {['timeline', 'actions', 'risks'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`px-4 py-3 font-medium transition-colors ${activeTab === tab
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-slate-400 hover:text-slate-200'
                }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <main className="px-6 py-8">
        <div className="max-w-7xl mx-auto">
          {activeTab === 'timeline' && selectedRun.changes && (
            <Timeline
              changes={selectedRun.changes}
              findings={selectedRun.findings_per_page?.items || []}
            />
          )}

          {activeTab === 'actions' && selectedRun.actions && (
            <ActionBoard actions={selectedRun.actions} />
          )}

          {activeTab === 'risks' && selectedRun.risks && (
            <RiskMatrix
              risks={selectedRun.risks}
              findings={selectedRun.findings_per_page?.items || []}
            />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;