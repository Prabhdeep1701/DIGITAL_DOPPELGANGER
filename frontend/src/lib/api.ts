const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

export async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json();
}

export function createWebSocket(path: string): WebSocket {
  return new WebSocket(`${WS_URL}${path}`);
}

// Session API
export const sessionsApi = {
  list: (params?: { limit?: number; classification?: string }) => {
    const qs = new URLSearchParams();
    if (params?.limit) qs.set('limit', String(params.limit));
    if (params?.classification) qs.set('classification', params.classification);
    return fetchApi<any[]>(`/api/sessions?${qs}`);
  },
  create: (data?: { is_simulated?: string }) =>
    fetchApi<{ session_id: string; user_id: string }>('/api/sessions', {
      method: 'POST',
      body: JSON.stringify(data || {}),
    }),
  get: (id: string) => fetchApi<any>(`/api/sessions/${id}`),
  end: (id: string) => fetchApi<any>(`/api/sessions/${id}/end`, { method: 'POST' }),
  dashboard: () => fetchApi<any>('/api/sessions/dashboard'),
  compare: (a: string, b: string) => fetchApi<any>(`/api/sessions/compare/${a}/${b}`),
};

// Events API
export const eventsApi = {
  create: (data: any) =>
    fetchApi<any>('/api/events', { method: 'POST', body: JSON.stringify(data) }),
  batch: (data: { events: any[] }) =>
    fetchApi<any>('/api/events/batch', { method: 'POST', body: JSON.stringify(data) }),
  getBySession: (sessionId: string) => fetchApi<any[]>(`/api/events/session/${sessionId}`),
};

// Automata API
export const automataApi = {
  definitions: () => fetchApi<any>('/api/automata/definitions'),
  processSequence: (events: any[]) =>
    fetchApi<any>('/api/automata/process-sequence', {
      method: 'POST',
      body: JSON.stringify(events),
    }),
  generateSequence: (type: string, length?: number) =>
    fetchApi<any>('/api/automata/generate-sequence', {
      method: 'POST',
      body: JSON.stringify({ sequence_type: type, length }),
    }),
  counterexample: (events: any[]) =>
    fetchApi<any>('/api/automata/counterexample', {
      method: 'POST',
      body: JSON.stringify(events),
    }),
};

// Simulator API
export const simulatorApi = {
  profiles: () => fetchApi<any>('/api/simulator/profiles'),
  run: (data: { profile: string; event_count?: number }) =>
    fetchApi<any>('/api/simulator/run', { method: 'POST', body: JSON.stringify(data) }),
  adversarial: (data: { test_type: string; event_count?: number }) =>
    fetchApi<any>('/api/simulator/adversarial', { method: 'POST', body: JSON.stringify(data) }),
};

// Experiments API
export const experimentsApi = {
  run: (data?: { human_count?: number; bot_count?: number; adversarial_count?: number }) =>
    fetchApi<any>('/api/experiments/run', {
      method: 'POST',
      body: JSON.stringify(data || {}),
    }),
};
