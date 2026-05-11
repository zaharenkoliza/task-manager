import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'

vi.mock('@/api/client', () => ({
	api: {
		statuses: {
			list: vi.fn().mockResolvedValue([
				{ id: 1, title: 'To Do' },
				{ id: 2, title: 'In Progress' },
			]),
		},
		priorities: {
			list: vi.fn().mockResolvedValue([
				{ id: 1, title: 'High' },
				{ id: 2, title: 'Normal' },
			]),
		},
		tasks: {
			list: vi.fn().mockResolvedValue([
				{
					id: 1,
					title: 'Test Task',
					description: 'Test description',
					status_id: 1,
					priority_id: 1,
					start_time: '2025-01-01T10:00:00',
					end_time: '2025-01-01T12:00:00',
					created_at: '2025-01-01T09:00:00',
					deleted_at: null,
				},
			]),
			delete: vi.fn().mockResolvedValue(undefined),
		},
	},
}))

import * as apiModule from '@/api/client'

beforeEach(() => {
	vi.clearAllMocks()
	vi.mocked(apiModule.api.statuses.list).mockResolvedValue([
		{ id: 1, title: 'To Do' },
		{ id: 2, title: 'In Progress' },
	])
	vi.mocked(apiModule.api.priorities.list).mockResolvedValue([
		{ id: 1, title: 'High' },
		{ id: 2, title: 'Normal' },
	])
	vi.mocked(apiModule.api.tasks.list).mockResolvedValue([
		{
			id: 1,
			title: 'Test Task',
			description: 'Test description',
			status_id: 1,
			priority_id: 1,
			start_time: '2025-01-01T10:00:00',
			end_time: '2025-01-01T12:00:00',
			created_at: '2025-01-01T09:00:00',
			deleted_at: null,
		},
	])
	vi.mocked(apiModule.api.tasks.delete).mockResolvedValue(undefined)
})

describe('App', () => {
	it('renders Task Manager title', async () => {
		render(<App />)
		expect(screen.getByText('Task Manager v2 Check!')).toBeInTheDocument()
	})

	it('renders New Task button', async () => {
		render(<App />)
		expect(screen.getByText('+ New Task')).toBeInTheDocument()
	})

	it('loads and displays tasks', async () => {
		render(<App />)
		await waitFor(() => {
			expect(screen.getByText('Test Task')).toBeInTheDocument()
		})
	})

	it('shows loading state initially', () => {
		render(<App />)
		expect(screen.getByText('Loading tasks…')).toBeInTheDocument()
	})

	it('opens create modal when New Task is clicked', async () => {
		const user = userEvent.setup()
		render(<App />)
		await waitFor(() => screen.getByText('Test Task'))
		await user.click(screen.getByText('+ New Task'))
		expect(screen.getByRole('heading', { name: /new task/i })).toBeInTheDocument()
	})

	it('opens edit modal when Edit is clicked', async () => {
		const user = userEvent.setup()
		render(<App />)
		await waitFor(() => screen.getByText('Test Task'))
		await user.click(screen.getByRole('button', { name: /edit/i }))
		expect(screen.getByRole('heading', { name: /edit task/i })).toBeInTheDocument()
	})

	it('closes modal when Cancel is clicked', async () => {
		const user = userEvent.setup()
		render(<App />)
		await waitFor(() => screen.getByText('Test Task'))
		await user.click(screen.getByText('+ New Task'))
		await user.click(screen.getByRole('button', { name: /cancel/i }))
		expect(screen.queryByRole('heading', { name: /new task/i })).not.toBeInTheDocument()
	})

	it('deletes task when Delete is confirmed', async () => {
		const user = userEvent.setup()
		vi.spyOn(window, 'confirm').mockReturnValue(true)
		render(<App />)
		await waitFor(() => screen.getByText('Test Task'))
		await user.click(screen.getByRole('button', { name: /delete/i }))
		expect(apiModule.api.tasks.delete).toHaveBeenCalledWith(1)
	})

	it('does not delete task when Delete is cancelled', async () => {
		const user = userEvent.setup()
		vi.spyOn(window, 'confirm').mockReturnValue(false)
		render(<App />)
		await waitFor(() => screen.getByText('Test Task'))
		await user.click(screen.getByRole('button', { name: /delete/i }))
		expect(apiModule.api.tasks.delete).not.toHaveBeenCalled()
	})

	it('shows error when tasks fail to load', async () => {
		vi.mocked(apiModule.api.tasks.list).mockRejectedValue(new Error('Network error'))
		render(<App />)
		await waitFor(() => {
			expect(screen.getByText('Network error')).toBeInTheDocument()
		})
	})

	it('dismisses error when close button clicked', async () => {
		const user = userEvent.setup()
		vi.mocked(apiModule.api.tasks.list).mockRejectedValue(new Error('Network error'))
		render(<App />)
		await waitFor(() => screen.getByText('Network error'))
		await user.click(screen.getByRole('button', { name: '✕' }))
		expect(screen.queryByText('Network error')).not.toBeInTheDocument()
	})
})
