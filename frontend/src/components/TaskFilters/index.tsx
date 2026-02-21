import type { TaskFilters as TaskFiltersType, TaskStatus, TaskPriority } from '@/types'
import styles from './TaskFilters.module.css'

interface TaskFiltersProps {
  filters: TaskFiltersType
  statuses: TaskStatus[]
  priorities: TaskPriority[]
  onChange: (f: TaskFiltersType) => void
}

export function TaskFilters({ filters, statuses, priorities, onChange }: TaskFiltersProps) {
	const hasFilters =
    filters.status_id != null ||
    filters.priority_id != null ||
    (filters.start_time?.length ?? 0) > 0 ||
    (filters.end_time?.length ?? 0) > 0

	const update = (key: keyof TaskFiltersType, value: string | number | undefined) => {
		const v = value === '' || value == null ? undefined : value
		onChange({ ...filters, [key]: v as never })
	}

	const clear = () => onChange({})

	return (
		<div className={styles.filters}>
			<div className={styles.field}>
				<label htmlFor="status-select">Status</label>
				<select
					value={filters.status_id ?? ''}
					onChange={(e) => update('status_id', e.target.value ? Number(e.target.value) : undefined)}
					id='status-select'
				>
					<option value="">All</option>
					{statuses.map((s) => (
						<option key={s.id} value={s.id}>
							{s.title}
						</option>
					))}
				</select>
			</div>
			<div className={styles.field}>
				<label htmlFor='priority-select'>Priority</label>
				<select
					value={filters.priority_id ?? ''}
					onChange={(e) => update('priority_id', e.target.value ? Number(e.target.value) : undefined)}
					id='priority-select'
				>
					<option value="">All</option>
					{priorities.map((p) => (
						<option key={p.id} value={p.id}>
							{p.title}
						</option>
					))}
				</select>
			</div>
			<div className={styles.field}>
				<label>From</label>
				<input
					type="datetime-local"
					value={filters.start_time ?? ''}
					onChange={(e) => update('start_time', e.target.value || undefined)}
				/>
			</div>
			<div className={styles.field}>
				<label>To</label>
				<input
					type="datetime-local"
					value={filters.end_time ?? ''}
					onChange={(e) => update('end_time', e.target.value || undefined)}
				/>
			</div>
			{hasFilters && (
				<button className={styles.clearBtn} onClick={clear}>
          Clear filters
				</button>
			)}
		</div>
	)
}
