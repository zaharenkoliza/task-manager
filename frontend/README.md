# Task Manager – Frontend

React + TypeScript + Vite frontend for the task-manager web app.

## Tech stack

- **React 18**
- **TypeScript**
- **Vite**
- **CSS modules** (`.module.css`)

## Setup

```bash
npm install
```

## Development

Start the dev server (with API proxy to backend):

```bash
npm run dev
```

App: http://localhost:5173  
API requests to `/api` are proxied to `http://localhost:8000`. Run the backend on port 8000.

## Build

```bash
npm run build
```

## Mock mode

While the backend is in development, mock data is used. Create `.env` with:

```
VITE_USE_MOCK_API=true
```

To switch to the real backend, set `VITE_USE_MOCK_API=false` or remove the variable.

## API

- **Statuses** – `GET /api/tasks/statuses` (To Do, In Progress, Done)
- **Priorities** – `GET /api/tasks/priorities` (High, Normal, Low)
- **Tasks** – full CRUD + filters (status_id, priority_id, start_time, end_time)
