export interface TaskStatus {
  id: number
  title: string
}

export interface TaskPriority {
  id: number
  title: string
}

export interface Task {
  id: number
  title: string
  description: string | null
  status_id: number
  priority_id: number
  start_time: string
  end_time: string
  created_at: string
  deleted_at: string | null
}

export interface TaskCreateInput {
  title: string
  description?: string
}

export interface TaskUpdateInput {
  title?: string
  description?: string
  start_time?: string
  end_time?: string
  status_id?: number
  priority_id?: number
}

export interface TaskFilters {
  status_id?: number
  priority_id?: number
  start_time?: string
  end_time?: string
}
