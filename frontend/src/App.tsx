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
		const load = async () => {
			try {
				const [s, p] = await Promise.all([api.statuses.list(), api.priorities.list()])
				setStatuses(s)
				setPriorities(p)
			} catch (e) {
				setError(e instanceof Error ? e.message : String(e))
			}
		}
		void load()
	}, [])

	useEffect(() => {
		const load = async () => {
			setLoading(true)
			try {
				const data = await api.tasks.list(filters)
				setTasks(data)
				setError(null)
			} catch (e) {
				setError(e instanceof Error ? e.message : String(e))
			} finally {
				setLoading(false)
			}
		}
		void load()
	}, [filters])

	const refreshTasks = async () => {
		try {
			const data = await api.tasks.list(filters)
			setTasks(data)
		} catch (e) {
			setError(e instanceof Error ? e.message : String(e))
		}
	}

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
			await refreshTasks()
		} catch (e) {
			setError(e instanceof Error ? e.message : String(e))
		}
	}

	const handleSaved = async () => {
		closeModal()
		await refreshTasks()
	}

	return (
		<div className={styles.app}>
			<header className={styles.header}>
				<h1 className={styles.title}>Task Manager v2 Check!</h1>
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
					onSaved={handleSaved}
				/>
			)}
		</div>
	)
}

export default App
