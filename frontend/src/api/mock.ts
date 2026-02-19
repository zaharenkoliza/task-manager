import type {
	Task,
	TaskCreateInput,
	TaskFilters,
	TaskPriority,
	TaskStatus,
	TaskUpdateInput,
} from '@/types'

const MOCK_STATUSES: TaskStatus[] = [
	{ id: 1, title: 'To Do' },
	{ id: 2, title: 'In Progress' },
	{ id: 3, title: 'Done' },
]

const MOCK_PRIORITIES: TaskPriority[] = [
	{ id: 1, title: 'High' },
	{ id: 2, title: 'Normal' },
	{ id: 3, title: 'Low' },
]

const now = () => new Date().toISOString()

const createTask = (
	id: number,
	overrides: Partial<Task> = {},
): Task => ({
	id,
	title: 'Sample Task',
	description: null,
	status_id: 1,
	priority_id: 2,
	start_time: now(),
	end_time: now(),
	created_at: now(),
	deleted_at: null,
	...overrides,
})

// In-memory task store (persists during session)
const mockTasks: Task[] = [
	createTask(1, {
		title: 'Setup project',
		description: 'Initialize backend and frontend',
		status_id: 3,
		priority_id: 1,
		start_time: '2025-02-18T10:00:00',
		end_time: '2025-02-18T12:00:00',
		created_at: '2025-02-18T09:00:00',
	}),
	createTask(2, {
		title: 'Implement API',
		description: 'REST endpoints for tasks, statuses, priorities',
		status_id: 2,
		priority_id: 1,
		start_time: '2025-02-19T09:00:00',
		end_time: '2025-02-19T17:00:00',
		created_at: '2025-02-18T14:00:00',
	}),
	createTask(3, {
		title: 'Add filters',
		description: 'Filter tasks by status and priority',
		status_id: 1,
		priority_id: 2,
		start_time: '2025-02-20T10:00:00',
		end_time: '2025-02-20T11:00:00',
		created_at: '2025-02-19T10:00:00',
	}),
]

let nextId = 4

const delay = (ms = 150) => new Promise((r) => setTimeout(r, ms))

function matchesFilters(task: Task, filters?: TaskFilters): boolean {
	if (!filters) return true
	if (filters.status_id != null && task.status_id !== filters.status_id) return false
	if (filters.priority_id != null && task.priority_id !== filters.priority_id) return false
	if (filters.start_time && task.start_time < filters.start_time) return false
	if (filters.end_time && task.end_time > filters.end_time) return false
	return true
}

export const mockApi = {
	statuses: {
		list: async (): Promise<TaskStatus[]> => {
			await delay()
			return [...MOCK_STATUSES]
		},
		get: async (id: number): Promise<TaskStatus> => {
			await delay()
			const s = MOCK_STATUSES.find((s) => s.id === id)
			if (!s) throw new Error('Status not found')
			return s
		},
	},
	priorities: {
		list: async (): Promise<TaskPriority[]> => {
			await delay()
			return [...MOCK_PRIORITIES]
		},
		get: async (id: number): Promise<TaskPriority> => {
			await delay()
			const p = MOCK_PRIORITIES.find((p) => p.id === id)
			if (!p) throw new Error('Priority not found')
			return p
		},
	},
	tasks: {
		list: async (filters?: TaskFilters): Promise<Task[]> => {
			await delay()
			return mockTasks.filter((t) => !t.deleted_at && matchesFilters(t, filters))
		},
		get: async (id: number): Promise<Task> => {
			await delay()
			const t = mockTasks.find((t) => t.id === id && !t.deleted_at)
			if (!t) throw new Error('Task not found')
			return { ...t }
		},
		create: async (body: TaskCreateInput): Promise<Task> => {
			await delay()
			const task: Task = {
				id: nextId++,
				title: body.title,
				description: body.description ?? null,
				status_id: 1,
				priority_id: 2,
				start_time: now(),
				end_time: now(),
				created_at: now(),
				deleted_at: null,
			}
			mockTasks.push(task)
			return { ...task }
		},
		update: async (id: number, body: TaskUpdateInput): Promise<Task> => {
			await delay()
			const idx = mockTasks.findIndex((t) => t.id === id && !t.deleted_at)
			if (idx < 0) throw new Error('Task not found')
			mockTasks[idx] = {
				...mockTasks[idx],
				...body,
				title: body.title ?? mockTasks[idx].title,
				description: body.description !== undefined ? body.description : mockTasks[idx].description,
			}
			return { ...mockTasks[idx] }
		},
		delete: async (id: number): Promise<void> => {
			await delay()
			const t = mockTasks.find((t) => t.id === id && !t.deleted_at)
			if (!t) throw new Error('Task not found')
			t.deleted_at = now()
		},
	},
}
