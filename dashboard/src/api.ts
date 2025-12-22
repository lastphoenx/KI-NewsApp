import axios from 'axios';
import type { Run } from './types';

const API_BASE = 'http://localhost:8008';

export const api = {
    async getRuns(): Promise<Run[]> {
        const { data } = await axios.get(`${API_BASE}/runs`);
        return data;
    },

    async getRun(id: number): Promise<Run> {
        const { data } = await axios.get(`${API_BASE}/runs/${id}`);
        return data;
    },
};
