import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from './client'

const mockFetch = vi.fn()
vi.stubGlobal('fetch', mockFetch)

function makeResponse(body: unknown, status = 200, contentType = 'application/json') {
	return {
		ok: status >= 200 && status < 300,
		status,
		headers: { get: () => contentType },
		json: () => Promise.resolve(body),
		text: () => Promise.resolve(typeof body === 'string' ? body : JSON.stringify(body)),
	} as unknown as Response
}

beforeEach(() => {
	mockFetch.mockReset()
})

describe('api.statuses', () => {
	it('list fetches statuses', async () => {
		const data = [{ id: 1, title: 'To Do' }]
		mockFetch.mockResolvedValue(makeResponse(data))
		const result = await api.statuses.list()
		expect(result).toEqual(data)
		expect(mockFetch).toHaveBeenCalledWith('/api/tasks/statuses')
	})

	it('get fetches single status', async () => {
		const data = { id: 1, title: 'To Do' }
		mockFetch.mockResolvedValue(makeResponse(data))
		const result = await api.statuses.get(1)
		expect(result).toEqual(data)
		expect(mockFetch).toHaveBeenCalledWith('/api/tasks/statuses/1')
	})
})

describe('api.priorities', () => {
	it('list fetches priorities', async () => {
		const data = [{ id: 1, title: 'High' }]
		mockFetch.mockResolvedValue(makeResponse(data))
		const result = await api.priorities.list()
		expect(result).toEqual(data)
	})

	it('get fetches single priority', async () => {
		const data = { id: 2, title: 'Normal' }
		mockFetch.mockResolvedValue(makeResponse(data))
		const result = await api.priorities.get(2)
		expect(result).toEqual(data)
	})
})

describe('api.tasks', () => {
	it('list fetches tasks without filters', async () => {
		const data = [{ id: 1, title: 'Task' }]
		mockFetch.mockResolvedValue(makeResponse(data))
		await api.tasks.list()
		expect(mockFetch).toHaveBeenCalledWith('/api/tasks')
	})

	it('list fetches tasks with status filter', async () => {
		mockFetch.mockResolvedValue(makeResponse([]))
		await api.tasks.list({ status_id: 1 })
		expect(mockFetch).toHaveBeenCalledWith('/api/tasks?status_id=1')
	})

	it('list fetches tasks with priority filter', async () => {
		mockFetch.mockResolvedValue(makeResponse([]))
		await api.tasks.list({ priority_id: 2 })
		expect(mockFetch).toHaveBeenCalledWith('/api/tasks?priority_id=2')
	})

	it('list fetches tasks with time filters', async () => {
		mockFetch.mockResolvedValue(makeResponse([]))
		await api.tasks.list({ start_time: '2025-01-01', end_time: '2025-12-31' })
		const url = mockFetch.mock.calls[0][0] as string
		expect(url).toContain('start_time=2025-01-01')
		expect(url).toContain('end_time=2025-12-31')
	})

	it('list fetches tasks with all filters', async () => {
		mockFetch.mockResolvedValue(makeResponse([]))
		await api.tasks.list({ status_id: 1, priority_id: 2, start_time: '2025-01-01', end_time: '2025-12-31' })
		const url = mockFetch.mock.calls[0][0] as string
		expect(url).toContain('status_id=1')
		expect(url).toContain('priority_id=2')
	})

	it('get fetches single task', async () => {
		const data = { id: 1, title: 'Task' }
		mockFetch.mockResolvedValue(makeResponse(data))
		const result = await api.tasks.get(1)
		expect(result).toEqual(data)
	})

	it('create posts new task', async () => {
		const data = { id: 1, title: 'New Task' }
		mockFetch.mockResolvedValue(makeResponse(data))
		const result = await api.tasks.create({ title: 'New Task' })
		expect(result).toEqual(data)
		expect(mockFetch).toHaveBeenCalledWith('/api/tasks', expect.objectContaining({ method: 'POST' }))
	})

	it('update patches task', async () => {
		const data = { id: 1, title: 'Updated' }
		mockFetch.mockResolvedValue(makeResponse(data))
		const result = await api.tasks.update(1, { title: 'Updated' })
		expect(result).toEqual(data)
		expect(mockFetch).toHaveBeenCalledWith('/api/tasks/1', expect.objectContaining({ method: 'PATCH' }))
	})

	it('delete sends DELETE request', async () => {
		mockFetch.mockResolvedValue(makeResponse(null, 204))
		await api.tasks.delete(1)
		expect(mockFetch).toHaveBeenCalledWith('/api/tasks/1', expect.objectContaining({ method: 'DELETE' }))
	})
})

describe('handleResponse errors', () => {
	it('throws on non-ok response with text', async () => {
		mockFetch.mockResolvedValue(makeResponse('Not found', 404, 'text/plain'))
		await expect(api.tasks.get(999)).rejects.toThrow('Not found')
	})

	it('throws with HTTP status when body is empty', async () => {
		mockFetch.mockResolvedValue({
			ok: false,
			status: 500,
			headers: { get: () => 'text/plain' },
			text: () => Promise.resolve(''),
		} as unknown as Response)
		await expect(api.tasks.get(1)).rejects.toThrow('HTTP 500')
	})

	it('returns text for non-json response', async () => {
		mockFetch.mockResolvedValue(makeResponse('plain text', 200, 'text/plain'))
		const result = await api.tasks.get(1)
		expect(result).toBe('plain text')
	})
})
