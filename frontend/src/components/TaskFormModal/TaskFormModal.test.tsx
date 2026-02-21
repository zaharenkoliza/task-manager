import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TaskFormModal } from './index'
import type { Task, TaskStatus, TaskPriority } from '@/types'
import * as api from '@/api/client'

const statuses: TaskStatus[] = [
	{ id: 1, title: 'To Do' },
	{ id: 2, title: 'In Progress' },
	{ id: 3, title: 'Done' },
]

const priorities: TaskPriority[] = [
	{ id: 1, title: 'High' },
	{ id: 2, title: 'Normal' },
	{ id: 3, title: 'Low' },
]

const mockTask: Task = {
	id: 1,
	title: 'Edit me',
	description: 'Some description',
	status_id: 2,
	priority_id: 1,
	start_time: '2025-02-18T10:00:00',
	end_time: '2025-02-18T12:00:00',
	created_at: '2025-02-18T09:00:00',
	deleted_at: null,
}

vi.mock('@/api/client', () => ({
	api: {
		tasks: {
			create: vi.fn().mockResolvedValue({}),
			update: vi.fn().mockResolvedValue({}),
		},
	},
}))

describe('TaskFormModal', () => {
	const onClose = vi.fn()
	const onSaved = vi.fn()

	beforeEach(() => {
		vi.clearAllMocks()
	})

	it('renders New Task for create mode', () => {
		render(
			<TaskFormModal
				task={null}
				statuses={statuses}
				priorities={priorities}
				onClose={onClose}
				onSaved={onSaved}
			/>,
		)
		expect(screen.getByRole('heading', { name: /new task/i })).toBeInTheDocument()
		expect(screen.getByRole('button', { name: /create/i })).toBeInTheDocument()
	})

	it('renders Edit Task for edit mode', () => {
		render(
			<TaskFormModal
				task={mockTask}
				statuses={statuses}
				priorities={priorities}
				onClose={onClose}
				onSaved={onSaved}
			/>,
		)
		expect(screen.getByRole('heading', { name: /edit task/i })).toBeInTheDocument()
		expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument()
		expect(screen.getByDisplayValue('Edit me')).toBeInTheDocument()
		expect(screen.getByDisplayValue('Some description')).toBeInTheDocument()
	})

	it('calls onClose when Cancel is clicked', async () => {
		const user = userEvent.setup()
		render(
			<TaskFormModal
				task={null}
				statuses={statuses}
				priorities={priorities}
				onClose={onClose}
				onSaved={onSaved}
			/>,
		)
		await user.click(screen.getByRole('button', { name: /cancel/i }))
		expect(onClose).toHaveBeenCalled()
	})

	it('calls onClose when Close button is clicked', async () => {
		const user = userEvent.setup()
		render(
			<TaskFormModal
				task={null}
				statuses={statuses}
				priorities={priorities}
				onClose={onClose}
				onSaved={onSaved}
			/>,
		)
		await user.click(screen.getByRole('button', { name: /close/i }))
		expect(onClose).toHaveBeenCalled()
	})

	it('calls api.tasks.create and onSaved when creating task', async () => {
		const user = userEvent.setup()
		render(
			<TaskFormModal
				task={null}
				statuses={statuses}
				priorities={priorities}
				onClose={onClose}
				onSaved={onSaved}
			/>,
		)
		await user.type(screen.getByLabelText(/title/i), 'New task title')
		await user.click(screen.getByRole('button', { name: /create/i }))
		expect(api.api.tasks.create).toHaveBeenCalledWith({
			title: 'New task title',
			description: undefined,
		})
		expect(onSaved).toHaveBeenCalled()
	})
})
