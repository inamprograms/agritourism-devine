# Agritourism Devine – Frontend

Frontend application for the Agritourism Devine Phase 1 MVP, built with React.  
This app provides the UI for farmer input, carbon credit estimation views, and buyer project discovery using dummy data.

## Tech Stack
- React (Vite)
- JavaScript
- Axios
- Supabase client
- React Router

## Prerequisites
- Node.js (v18 or later)
- npm

## Local Setup

1. Navigate to the frontend directory
    ```bash
        cd frontend
    ```
2. Install dependencies
    ```bash
        npm install
    ```
3. Environment variables <br>
    Create a `.env` file in the frontend directory by copying the example file:

    ```bash
        cp .env.example .env
    ```
    Update `.env` with the required values:

    ```bash
        VITE_BACKEND_URL=http://localhost:5000
        VITE_SUPABASE_URL=your_supabase_project_url
        VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
    ```
   
4. Start the development server
   
    ```bash
    npm run dev
    ```
The frontend will be available at: `http://localhost:5173`

