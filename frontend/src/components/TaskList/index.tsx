import type { Task, TaskStatus, TaskPriority } from '@/types'
import styles from './TaskList.module.css'

interface TaskListProps {
  tasks: Task[]
  statuses: TaskStatus[]
  priorities: TaskPriority[]
  onEdit: (task: Task) => void
  onDelete: (id: number) => void
}

function formatDate(s: string) {
	try {
		const d = new Date(s)
		return isNaN(d.getTime()) ? s : d.toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' })
	} catch {
		return s
	}
}

function statusClass(title: string) {
	const t = title.toLowerCase()
	if (t.includes('progress')) return styles.statusInProgress
	if (t.includes('done')) return styles.statusDone
	return styles.statusToDo
}

function priorityClass(title: string) {
	const t = title.toLowerCase()
	if (t === 'high') return styles.priorityHigh
	if (t === 'low') return styles.priorityLow
	return styles.priorityNormal
}

export function TaskList({ tasks, statuses, priorities, onEdit, onDelete }: TaskListProps) {
	const statusMap = Object.fromEntries(statuses.map((s) => [s.id, s]))
	const priorityMap = Object.fromEntries(priorities.map((p) => [p.id, p]))

	if (tasks.length === 0) {
		return <p className={styles.empty}>No tasks yet. Create your first task above.</p>
	}

	return (
		<ul className={styles.list}>
			{tasks.map((task) => {
				const status = statusMap[task.status_id]
				const priority = priorityMap[task.priority_id]
				return (
					<li key={task.id} className={styles.item}>
						<div className={styles.info}>
							<h3 className={styles.title}>{task.title}</h3>
							{task.description && <p className={styles.description}>{task.description}</p>}
						</div>
						<div>
							{status && (
								<span className={`${styles.badge} ${statusClass(status.title)}`}>
									{status.title}
								</span>
							)}
						</div>
						<div>
							{priority && (
								<span className={`${styles.badge} ${priorityClass(priority.title)}`}>
									{priority.title}
								</span>
							)}
						</div>
						<div className={styles.actions}>
							<span className={styles.dates}>
								{formatDate(task.start_time)} → {formatDate(task.end_time)}
							</span>
							<button className={styles.btn} onClick={() => onEdit(task)}>
                Edit
							</button>
							<button className={`${styles.btn} ${styles.btnDanger}`} onClick={() => onDelete(task.id)}>
                Delete
							</button>
						</div>
					</li>
				)
			})}
		</ul>
	)
}
