import type { Task, TaskCreateInput, TaskFilters, TaskPriority, TaskStatus, TaskUpdateInput } from '@/types'

const BASE = '/api'

async function handleResponse<T>(res: Response): Promise<T> {
	if (!res.ok) {
		const text = await res.text()
		throw new Error(text || `HTTP ${res.status}`)
	}
	if (res.status === 204) {
		return undefined as T
	}
	const contentType = res.headers.get('content-type')
	if (contentType?.includes('application/json')) {
		return res.json() as Promise<T>
	}
	return res.text() as unknown as T
}

export const api = {
	statuses: {
		list: () => fetch(`${BASE}/tasks/statuses`).then((r) => handleResponse<TaskStatus[]>(r)),
		get: (id: number) => fetch(`${BASE}/tasks/statuses/${id}`).then((r) => handleResponse<TaskStatus>(r)),
	},
	priorities: {
		list: () => fetch(`${BASE}/tasks/priorities`).then((r) => handleResponse<TaskPriority[]>(r)),
		get: (id: number) =>
			fetch(`${BASE}/tasks/priorities/${id}`).then((r) => handleResponse<TaskPriority>(r)),
	},
	tasks: {
		list: (filters?: TaskFilters) => {
			const params = new URLSearchParams()
			if (filters?.status_id != null) params.set('status_id', String(filters.status_id))
			if (filters?.priority_id != null) params.set('priority_id', String(filters.priority_id))
			if (filters?.start_time) params.set('start_time', filters.start_time)
			if (filters?.end_time) params.set('end_time', filters.end_time)
			const qs = params.toString()
			const url = `${BASE}/tasks${qs ? `?${qs}` : ''}`
			return fetch(url).then((r) => handleResponse<Task[]>(r))
		},
		get: (id: number) => fetch(`${BASE}/tasks/${id}`).then((r) => handleResponse<Task>(r)),
		create: (body: TaskCreateInput) =>
			fetch(`${BASE}/tasks`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(body),
			}).then((r) => handleResponse<Task>(r)),
		update: (id: number, body: TaskUpdateInput) =>
			fetch(`${BASE}/tasks/${id}`, {
				method: 'PATCH',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(body),
			}).then((r) => handleResponse<Task>(r)),
		delete: (id: number) =>
			fetch(`${BASE}/tasks/${id}`, { method: 'DELETE' }).then((r) => handleResponse<void>(r)),
	},
}
