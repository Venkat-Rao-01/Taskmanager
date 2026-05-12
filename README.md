# TaskFlow

TaskFlow is a full-stack team task manager built with React, FastAPI, and MongoDB. It supports authentication, project and team management, task assignment, progress tracking, overdue task monitoring, and role-based access for Admin and Member users.

## Features

- Signup and login with JWT authentication
- First registered user becomes Admin automatically
- Admins can create projects and assign members
- Project members can create and update their own assigned tasks
- Task statuses: To Do, In Progress, Review, Done
- Dashboard with project count, task count, completed tasks, overdue tasks, and upcoming work
- Corporate responsive UI built for demo and recruiter review
- FastAPI Swagger documentation at `/docs`

## Tech Stack

- Frontend: React, Vite, CSS
- Backend: FastAPI, Motor, Pydantic, JWT
- Database: MongoDB or MongoDB Atlas
- Deployment: Railway

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

## Environment Variables

Backend:

```env
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=taskflow
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:5173
```

Frontend:

```env
VITE_API_URL=http://localhost:8000/api
```

## Railway Deployment

1. Push this project to GitHub.
2. Create a MongoDB Atlas free cluster and copy the connection string.
3. Create one Railway service for the backend.
4. Set the backend root directory to `backend`.
5. Add backend environment variables:
   - `MONGODB_URI`
   - `DATABASE_NAME`
   - `JWT_SECRET_KEY`
   - `JWT_ALGORITHM`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`
   - `CORS_ORIGINS`
   Do not upload `backend/.env` to GitHub. Add these values only inside Railway variables.
6. Create one Railway service for the frontend.
7. Set the frontend root directory to `frontend`.
8. Add frontend environment variable:
   - `VITE_API_URL=https://your-backend-service.up.railway.app/api`
9. Update backend `CORS_ORIGINS` with your deployed frontend URL.
10. Open the frontend URL, sign up, and create your first project.

## Demo Video Checklist

- Show signup and mention first user becomes Admin
- Show FastAPI `/docs`
- Create a project and assign members
- Create a task with priority and due date
- Move the task across statuses
- Show dashboard metrics and overdue highlighting
- End with the live Railway URL and GitHub repository

## Author

GitHub: [sathwikagannamaneni](https://github.com/sathwikagannamaneni)
