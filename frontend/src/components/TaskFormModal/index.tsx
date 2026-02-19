import { useState, useEffect } from 'react'
import { api } from '@/api/client'
import type { Task, TaskStatus, TaskPriority } from '@/types'
import styles from './TaskFormModal.module.css'

function toInputDatetime(s: string | null | undefined): string {
	if (!s) return ''
	try {
		const d = new Date(s)
		if (isNaN(d.getTime())) return ''
		const pad = (n: number) => String(n).padStart(2, '0')
		return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
	} catch {
		return ''
	}
}

function fromInputDatetime(s: string): string | undefined {
	if (!s?.trim()) return undefined
	const d = new Date(s)
	return isNaN(d.getTime()) ? undefined : d.toISOString()
}

interface TaskFormModalProps {
  task: Task | null
  statuses: TaskStatus[]
  priorities: TaskPriority[]
  onClose: () => void
  onSaved: () => void
}

export function TaskFormModal({ task, statuses, priorities, onClose, onSaved }: TaskFormModalProps) {
	const [title, setTitle] = useState('')
	const [description, setDescription] = useState('')
	const [statusId, setStatusId] = useState<number | ''>('')
	const [priorityId, setPriorityId] = useState<number | ''>('')
	const [startTime, setStartTime] = useState('')
	const [endTime, setEndTime] = useState('')
	const [saving, setSaving] = useState(false)
	const [error, setError] = useState<string | null>(null)

	const isEdit = !!task

	useEffect(() => {
		if (task) {
			setTitle(task.title)
			setDescription(task.description ?? '')
			setStatusId(task.status_id)
			setPriorityId(task.priority_id)
			setStartTime(toInputDatetime(task.start_time))
			setEndTime(toInputDatetime(task.end_time))
		} else {
			setTitle('')
			setDescription('')
			setStatusId(statuses[0]?.id ?? '')
			setPriorityId(priorities[0]?.id ?? '')
			const now = new Date()
			const later = new Date(now.getTime() + 60 * 60 * 1000)
			setStartTime(toInputDatetime(now.toISOString()))
			setEndTime(toInputDatetime(later.toISOString()))
		}
		setError(null)
	}, [task, statuses, priorities])

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault()
		setError(null)
		const t = title.trim()
		if (!t) {
			setError('Title is required')
			return
		}
		setSaving(true)
		try {
			if (isEdit && task) {
				await api.tasks.update(task.id, {
					title: t,
					description: description.trim() || undefined,
					status_id: statusId || undefined,
					priority_id: priorityId || undefined,
					start_time: fromInputDatetime(startTime),
					end_time: fromInputDatetime(endTime),
				})
			} else {
				await api.tasks.create({
					title: t,
					description: description.trim() || undefined,
				})
			}
			onSaved()
		} catch (err) {
			setError(String(err instanceof Error ? err.message : err))
		} finally {
			setSaving(false)
		}
	}

	return (
		<div className={styles.overlay} onClick={onClose}>
			<div className={styles.modal} onClick={(e) => e.stopPropagation()}>
				<div className={styles.header}>
					<h2>{isEdit ? 'Edit Task' : 'New Task'}</h2>
					<button type="button" className={styles.closeBtn} onClick={onClose} aria-label="Close">
            ✕
					</button>
				</div>

				<form className={styles.form} onSubmit={handleSubmit}>
					{error && (
						<div style={{ color: 'var(--color-danger)', fontSize: '0.9rem' }}>{error}</div>
					)}
					<div className={styles.field}>
						<label htmlFor="title">Title *</label>
						<input
							id="title"
							value={title}
							onChange={(e) => setTitle(e.target.value)}
							placeholder="Task title"
							required
						/>
					</div>
					<div className={styles.field}>
						<label htmlFor="description">Description</label>
						<textarea
							id="description"
							value={description}
							onChange={(e) => setDescription(e.target.value)}
							placeholder="Optional description"
						/>
					</div>
					{isEdit && (
						<>
							<div className={styles.field}>
								<label htmlFor="status">Status</label>
								<select
									id="status"
									value={statusId}
									onChange={(e) => setStatusId(e.target.value ? Number(e.target.value) : '')}
								>
									{statuses.map((s) => (
										<option key={s.id} value={s.id}>
											{s.title}
										</option>
									))}
								</select>
							</div>
							<div className={styles.field}>
								<label htmlFor="priority">Priority</label>
								<select
									id="priority"
									value={priorityId}
									onChange={(e) => setPriorityId(e.target.value ? Number(e.target.value) : '')}
								>
									{priorities.map((p) => (
										<option key={p.id} value={p.id}>
											{p.title}
										</option>
									))}
								</select>
							</div>
							<div className={styles.field}>
								<label htmlFor="start">Start time</label>
								<input
									id="start"
									type="datetime-local"
									value={startTime}
									onChange={(e) => setStartTime(e.target.value)}
								/>
							</div>
							<div className={styles.field}>
								<label htmlFor="end">End time</label>
								<input
									id="end"
									type="datetime-local"
									value={endTime}
									onChange={(e) => setEndTime(e.target.value)}
								/>
							</div>
						</>
					)}
					<div className={styles.footer}>
						<button type="button" className={styles.btnSecondary} onClick={onClose}>
              Cancel
						</button>
						<button type="submit" className={styles.btnPrimary} disabled={saving}>
							{saving ? 'Saving…' : isEdit ? 'Save' : 'Create'}
						</button>
					</div>
				</form>
			</div>
		</div>
	)
}
