# Deploying ProcurePilot

This guide explains how to deploy the ProcurePilot application with the frontend on **Vercel** and the backend on **Hugging Face Spaces** using Docker.

## 1. Deploying the Backend to Hugging Face Spaces

Hugging Face Spaces provides a free Docker hosting environment that is perfect for FastAPI applications.

### Prerequisites
- Create an account on [Hugging Face](https://huggingface.co/).
- Create a new **Space** and select **Docker** as the SDK.
- Choose a Blank Docker template.

### Setup Steps
1. Clone or copy the contents of the `apps/api` folder into your Hugging Face Space repository.
2. Ensure the `Dockerfile` and `requirements.txt` are at the root of the Space repository.
3. Hugging Face Spaces will automatically build the Docker image and start the application.

### Environment Variables
In your Hugging Face Space, go to **Settings** -> **Variables and secrets**. Add the following **Secrets**:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `PROCUREPILOT_GROQ_API_KEY` | Your Groq API key | `gsk_...` |
| `PROCUREPILOT_CORS_ORIGINS` | Allowed frontend URLs | `https://your-app.vercel.app,http://localhost:3000` |
| `PROCUREPILOT_ENV` | Environment name | `production` |

Once added, the Space will automatically restart. Note the URL of your space (e.g., `https://your-username-procurepilot.hf.space`).

---

## 2. Deploying the Frontend to Vercel

Vercel is the optimal hosting platform for Next.js applications.

### Setup Steps
1. Push your `apps/web` code to a GitHub repository.
2. Log into [Vercel](https://vercel.com/) and create a **New Project**.
3. Import the repository.
4. If your repository contains both frontend and backend, set the **Root Directory** to `apps/web`.
5. Vercel will auto-detect Next.js. 

### Environment Variables
Before clicking Deploy, add the following Environment Variable:

| Variable Name | Description | Example |
|---------------|-------------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | The URL of your backend | `https://your-username-procurepilot.hf.space` |

### Finalizing
Click **Deploy**. Vercel will build and deploy the frontend. 

Once deployed, copy the final Vercel domain (e.g., `https://procurepilot-demo.vercel.app`) and update the `PROCUREPILOT_CORS_ORIGINS` secret in your Hugging Face backend to include this URL.

---

## Production Checks
- Verify backend health: Go to `https://<your-hf-space-url>/api/v1/health/live`. It should return `{"status":"ok"}`.
- Verify frontend: Open your Vercel URL and submit a test procurement request.
