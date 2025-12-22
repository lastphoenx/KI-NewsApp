export interface Run {
    id: number;
    template_id: number;
    status: string;
    relevance_score: number | null;
    summary: {
        pages_analyzed: number;
        avg_page_score: number;
        ai_provider?: string;
        ai_model?: string;
    } | null;
    changes: Change[] | null;
    actions: Action[] | null;
    risks: Risk[] | null;
    findings_per_page: {
        items: Finding[];
    } | null;
    created_at: string | null;
    finished_at: string | null;
}

export interface Change {
    topic: string;
    description: string;
    effective_date: string;
    impact: 'high' | 'medium' | 'low';
    affected_interfaces: string[];
    spec_reference: string;
    change_type: string;
}

export interface Action {
    action: string;
    priority: 'high' | 'medium' | 'low';
    deadline: string;
    effort: string;
    owner_role: string;
    reason: string;
    dependencies: string[];
}

export interface Risk {
    risk: string;
    area: 'Business' | 'Tech' | 'Compliance' | 'Ops';
    severity: 'high' | 'medium' | 'low';
    likelihood: 'high' | 'medium' | 'low';
    consequence: string;
    mitigation: string;
    detection: string;
}

export interface Finding {
    url: string;
    status: number;
    content_type?: string;
    title?: string;
    page_relevance: number;
    key_findings: string[];
    keyword_details: Record<string, number>;
}
