import { useEffect, useState } from 'react'
import { api } from './api/client'
import type { Task, TaskFilters as TaskFiltersType, TaskStatus, TaskPriority } from './types'
import { TaskList } from './components/TaskList'
import { TaskFilters } from './components/TaskFilters'
import { TaskFormModal } from './components/TaskFormModal'
import styles from './App.module.css'

function App() {
	const [tasks, setTasks] = useState<Task[]>([])
	const [statuses, setStatuses] = useState<TaskStatus[]>([])
	const [priorities, setPriorities] = useState<TaskPriority[]>([])
	const [filters, setFilters] = useState<TaskFiltersType>({})
	const [loading, setLoading] = useState(true)
	const [error, setError] = useState<string | null>(null)
	const [modalOpen, setModalOpen] = useState(false)
	const [editingTask, setEditingTask] = useState<Task | null>(null)

	useEffect(() => {
		Promise.all([api.statuses.list(), api.priorities.list()])
			.then(([s, p]) => {
				setStatuses(s)
				setPriorities(p)
			})
			.catch((e) => setError(String(e?.message ?? e)))
	}, [])

	useEffect(() => {
		setLoading(true)
		api.tasks
			.list(filters)
			.then((data) => {
				setTasks(data)
				setError(null)
			})
			.catch((e) => setError(String(e?.message ?? e)))
			.finally(() => setLoading(false))
	}, [filters])

	const refreshTasks = () =>
		api.tasks.list(filters).then(setTasks).catch((e) => setError(String(e?.message ?? e)))

	const openCreate = () => {
		setEditingTask(null)
		setModalOpen(true)
	}

	const openEdit = (task: Task) => {
		setEditingTask(task)
		setModalOpen(true)
	}

	const closeModal = () => {
		setModalOpen(false)
		setEditingTask(null)
	}

	const handleDelete = async (id: number) => {
		if (!confirm('Delete this task?')) return
		try {
			await api.tasks.delete(id)
			refreshTasks()
		} catch (e) {
			setError(String(e?.message ?? e))
		}
	}

	return (
		<div className={styles.app}>
			<header className={styles.header}>
				<h1 className={styles.title}>Task Manager</h1>
				<button className={styles.addBtn} onClick={openCreate}>
          + New Task
				</button>
			</header>

			{error && (
				<div className={styles.error}>
					{error}
					<button onClick={() => setError(null)}>✕</button>
				</div>
			)}

			<TaskFilters
				filters={filters}
				statuses={statuses}
				priorities={priorities}
				onChange={setFilters}
			/>

			<main className={styles.main}>
				{loading ? (
					<p className={styles.loading}>Loading tasks…</p>
				) : (
					<TaskList
						tasks={tasks}
						statuses={statuses}
						priorities={priorities}
						onEdit={openEdit}
						onDelete={handleDelete}
					/>
				)}
			</main>

			{modalOpen && (
				<TaskFormModal
					task={editingTask}
					statuses={statuses}
					priorities={priorities}
					onClose={closeModal}
					onSaved={() => {
						closeModal()
						refreshTasks()
					}}
				/>
			)}
		</div>
	)
}

export default App
