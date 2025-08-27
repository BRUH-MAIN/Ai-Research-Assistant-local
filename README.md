## Ai-Research-Assistant-local

This project is an AI-powered research assistant platform designed to facilitate collaborative research, chat, and data management. It features:

- **Group Chat with AI Paper Analysis:** Collaborate in groups where users can discuss and analyze research papers with AI assistance, enabling deeper insights and automated summarization.
- **AI-Powered Search:** Quickly find relevant research papers, chat history, and data using intelligent search algorithms.

The platform is built with a strong focus on DevOps, ensuring scalable, reliable, and maintainable deployments.

### Features
- **Dual Database Support:** Integrates both Redis and PostgreSQL for fast caching and persistent storage.
- **Group Chat & AI Paper Analysis:** Real-time group chat with automated research paper analysis and summarization.
- **AI-Powered Search:** Intelligent search for papers, chat, and data.
- **DevOps Ready:** Dockerized services, CI/CD support, environment configuration, and scalable architecture for production-grade deployments.
- **Synchronization:** Redis-Postgres sync for data consistency and performance.
- **RESTful API:** Organized under `backend/app/api/v1/` for chat, feedback, users, groups, and more.
- **Frontend:** Built with Next.js and Tailwind CSS for a responsive, user-friendly interface.

### Project Structure
- `backend/`: Python FastAPI backend with modular apps for API, core config, database management, models, and services.
- `frontend/`: Next.js frontend with reusable components, hooks, and service integrations.
- `db/`: Database management scripts and utilities.
- `docker-compose.yml`, `Dockerfile.*`: Containerization for easy deployment and scaling.

### Getting Started
1. Clone the repository.
2. Use Docker Compose to start backend and frontend services, or integrate with your CI/CD pipeline for automated deployments.
3. Configure environment variables and database connections as needed. All services are containerized for easy scaling and management.

### Technologies Used
- Python, FastAPI, Redis, PostgreSQL
- Next.js, React, Tailwind CSS
- Docker, Docker Compose

### Documentation
See backend and frontend README files for detailed setup and usage instructions.
