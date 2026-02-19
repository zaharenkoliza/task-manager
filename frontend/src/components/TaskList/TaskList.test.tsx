import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TaskList } from './index'
import type { Task, TaskStatus, TaskPriority } from '@/types'

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

const mockTasks: Task[] = [
	{
		id: 1,
		title: 'First task',
		description: 'Description one',
		status_id: 1,
		priority_id: 2,
		start_time: '2025-02-18T10:00:00',
		end_time: '2025-02-18T12:00:00',
		created_at: '2025-02-18T09:00:00',
		deleted_at: null,
	},
	{
		id: 2,
		title: 'Second task',
		description: null,
		status_id: 2,
		priority_id: 1,
		start_time: '2025-02-19T09:00:00',
		end_time: '2025-02-19T17:00:00',
		created_at: '2025-02-18T14:00:00',
		deleted_at: null,
	},
]

describe('TaskList', () => {
	it('renders empty state when no tasks', () => {
		render(
			<TaskList tasks={[]} statuses={statuses} priorities={priorities} onEdit={vi.fn()} onDelete={vi.fn()} />,
		)
		expect(screen.getByText('No tasks yet. Create your first task above.')).toBeInTheDocument()
	})

	it('renders all tasks with titles and descriptions', () => {
		render(
			<TaskList
				tasks={mockTasks}
				statuses={statuses}
				priorities={priorities}
				onEdit={vi.fn()}
				onDelete={vi.fn()}
			/>,
		)
		expect(screen.getByText('First task')).toBeInTheDocument()
		expect(screen.getByText('Description one')).toBeInTheDocument()
		expect(screen.getByText('Second task')).toBeInTheDocument()
	})

	it('renders status and priority badges', () => {
		render(
			<TaskList
				tasks={mockTasks}
				statuses={statuses}
				priorities={priorities}
				onEdit={vi.fn()}
				onDelete={vi.fn()}
			/>,
		)
		expect(screen.getByText('To Do')).toBeInTheDocument()
		expect(screen.getByText('In Progress')).toBeInTheDocument()
		expect(screen.getByText('High')).toBeInTheDocument()
		expect(screen.getByText('Normal')).toBeInTheDocument()
	})

	it('calls onEdit when Edit button is clicked', async () => {
		const onEdit = vi.fn()
		const user = userEvent.setup()
		render(
			<TaskList
				tasks={mockTasks}
				statuses={statuses}
				priorities={priorities}
				onEdit={onEdit}
				onDelete={vi.fn()}
			/>,
		)
		const editButtons = screen.getAllByRole('button', { name: /edit/i })
		await user.click(editButtons[0])
		expect(onEdit).toHaveBeenCalledWith(mockTasks[0])
	})

	it('calls onDelete when Delete button is clicked', async () => {
		const onDelete = vi.fn()
		const user = userEvent.setup()
		render(
			<TaskList
				tasks={mockTasks}
				statuses={statuses}
				priorities={priorities}
				onEdit={vi.fn()}
				onDelete={onDelete}
			/>,
		)
		const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
		await user.click(deleteButtons[0])
		expect(onDelete).toHaveBeenCalledWith(1)
	})
})
