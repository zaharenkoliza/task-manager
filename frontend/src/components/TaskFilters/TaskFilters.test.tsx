import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TaskFilters } from './index'
import type { TaskStatus, TaskPriority } from '@/types'

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

describe('TaskFilters', () => {
	it('renders status, priority, from and to filter fields', () => {
		const onChange = vi.fn()
		render(
			<TaskFilters filters={{}} statuses={statuses} priorities={priorities} onChange={onChange} />,
		)
		expect(screen.getByText('Status')).toBeInTheDocument()
		expect(screen.getByText('Priority')).toBeInTheDocument()
		expect(screen.getByText('From')).toBeInTheDocument()
		expect(screen.getByText('To')).toBeInTheDocument()
		expect(screen.getByLabelText('Status')).toBeInTheDocument()
		expect(screen.getByLabelText('Priority')).toBeInTheDocument()
	})

	it('does not show Clear filters when no filters applied', () => {
		render(
			<TaskFilters filters={{}} statuses={statuses} priorities={priorities} onChange={vi.fn()} />,
		)
		expect(screen.queryByText('Clear filters')).not.toBeInTheDocument()
	})

	it('shows Clear filters when filters are applied', () => {
		render(
			<TaskFilters
				filters={{ status_id: 1 }}
				statuses={statuses}
				priorities={priorities}
				onChange={vi.fn()}
			/>,
		)
		expect(screen.getByText('Clear filters')).toBeInTheDocument()
	})

	it('calls onChange when status is selected', async () => {
		const onChange = vi.fn()
		const user = userEvent.setup()
		render(
			<TaskFilters filters={{}} statuses={statuses} priorities={priorities} onChange={onChange} />,
		)
		const statusSelect = screen.getByLabelText('Status')
		await user.selectOptions(statusSelect, '2')
		expect(onChange).toHaveBeenCalledWith({ status_id: 2 })
	})

	it('calls onChange with empty object when Clear filters is clicked', async () => {
		const onChange = vi.fn()
		const user = userEvent.setup()
		render(
			<TaskFilters
				filters={{ status_id: 1, priority_id: 2 }}
				statuses={statuses}
				priorities={priorities}
				onChange={onChange}
			/>,
		)
		await user.click(screen.getByText('Clear filters'))
		expect(onChange).toHaveBeenCalledWith({})
	})
})
