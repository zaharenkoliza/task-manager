import { describe, it, expect } from 'vitest'
import { mockApi } from './mock'

describe('mockApi', () => {
	describe('statuses', () => {
		it('returns statuses list', async () => {
			const list = await mockApi.statuses.list()
			expect(list).toHaveLength(3)
			expect(list.map((s) => s.title)).toEqual(['To Do', 'In Progress', 'Done'])
		})

		it('returns single status by id', async () => {
			const s = await mockApi.statuses.get(1)
			expect(s).toEqual({ id: 1, title: 'To Do' })
		})

		it('throws for invalid status id', async () => {
			await expect(mockApi.statuses.get(99)).rejects.toThrow('Status not found')
		})
	})

	describe('priorities', () => {
		it('returns priorities list', async () => {
			const list = await mockApi.priorities.list()
			expect(list).toHaveLength(3)
			expect(list.map((p) => p.title)).toEqual(['High', 'Normal', 'Low'])
		})

		it('returns single priority by id', async () => {
			const p = await mockApi.priorities.get(2)
			expect(p).toEqual({ id: 2, title: 'Normal' })
		})

		it('throws for invalid priority id', async () => {
			await expect(mockApi.priorities.get(99)).rejects.toThrow('Priority not found')
		})
	})

	describe('tasks', () => {
		it('returns tasks list', async () => {
			const list = await mockApi.tasks.list()
			expect(list.length).toBeGreaterThanOrEqual(3)
			expect(list.every((t) => t.title && t.id && t.status_id && t.priority_id)).toBe(true)
		})

		it('filters tasks by status_id', async () => {
			const list = await mockApi.tasks.list({ status_id: 3 })
			expect(list.every((t) => t.status_id === 3)).toBe(true)
		})

		it('filters tasks by priority_id', async () => {
			const list = await mockApi.tasks.list({ priority_id: 1 })
			expect(list.every((t) => t.priority_id === 1)).toBe(true)
		})

		it('creates a new task', async () => {
			const task = await mockApi.tasks.create({ title: 'Test task', description: 'Test desc' })
			expect(task.title).toBe('Test task')
			expect(task.description).toBe('Test desc')
			expect(task.id).toBeDefined()
			expect(task.status_id).toBe(1)
			expect(task.priority_id).toBe(2)
		})

		it('updates a task', async () => {
			const created = await mockApi.tasks.create({ title: 'Original' })
			const updated = await mockApi.tasks.update(created.id, { title: 'Updated title' })
			expect(updated.title).toBe('Updated title')
		})

		it('deletes a task (soft delete)', async () => {
			const created = await mockApi.tasks.create({ title: 'To delete' })
			await mockApi.tasks.delete(created.id)
			const list = await mockApi.tasks.list()
			expect(list.find((t) => t.id === created.id)).toBeUndefined()
		})
	})
})
