# Portfolio Chatbot Backend API

A robust backend API for a portfolio chatbot, built using Django and deployed on the EC2 cloud platform with Docker. This API powers my personal portfolio website chatbot, providing intelligent chatbot responses by leveraging Retrieval-Augmented Generation (RAG) and a Large Language Model (LLM) with advanced prompt engineering techniques.

## Overview

This project serves as the backend for my personal portfolio chatbot. It processes user inputs, retrieves relevant documents using RAG, and generates professional, clean responses via an LLM. The application is optimized with Redis for session and message management, monitored with Grafana Loki for logging, and includes a healthcheck endpoint for uptime monitoring.

### Key Features
- **Framework**: Built with Django for a scalable and secure backend.
- **Deployment**: Hosted on AWS EC2 using Docker for containerized deployment.
- **Chatbot Logic**: Utilizes Retrieval-Augmented Generation (RAG) to fetch relevant documents and an LLM with prompt engineering for polished responses.
- **Caching**: Redis is used to manage sessions and store chatbot/user messages efficiently.
- **Logging**: Grafana Loki is integrated for application log management and troubleshooting.
- **Monitoring**: A healthcheck endpoint is mapped to UptimeRobot for real-time service availability alerts.

## Architecture

1. **User Input**: The API receives queries from the portfolio website.
2. **RAG Process**: Relevant documents are retrieved based on the user query.
3. **LLM Response**: A professional response is generated using an LLM with custom prompt techniques.
4. **Caching**: Redis stores session data and messages for quick access.
5. **Logging**: Application logs are sent to Grafana Loki for monitoring and debugging.
6. **Healthcheck**: A dedicated endpoint ensures uptime monitoring via UptimeRobot.

## Tech Stack
- **Backend**: Django
- **Containerization**: Docker
- **Hosting**: AWS EC2
- **Caching**: Redis
- **Logging**: Grafana Loki
- **Monitoring**: UptimeRobot
- **AI**: RAG + LLM (with prompt engineering)

## Setup and Installation

### Prerequisites
- Docker
- AWS EC2 instance
- Redis server
- Grafana Loki setup
- UptimeRobot account

### Deployment Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Shivam-Shane/Portfolio_Backend.git
   cd Portfolio_Backend
   Configure environment variables (e.g., Redis URL, LLM API keys) in a .env file.
   run locally python manage.py runserver 0.0.0.0:3003
2. Build and run the Docker container:
    ```bash
    docker build -t portfolio-chatbot-api .
    docker run -d -p 8000:8000 portfolio-chatbot-api
3. Set up [Grafana Loki](https://grafana.com/resources/log-monitoring/) for logging and [UptimeRobot](https://uptimerobot.com/keyword-monitoring/) for        healthcheck monitoring.

4. API Endpoints
    - Healthcheck: GET api/healthcheck - Returns the status of the service.
    - Chatbot: POST api/chat_worker/ - Accepts user input and returns a generated response.

## Monitoring and Logging
- UptimeRobot: Monitors the /healthcheck endpoint and sends alerts if the service is down.
- Grafana Loki: Stores and visualizes logs for debugging and performance tracking.

## Contributing

This is a personal portfolio project, but I’m open to suggestions! Feel free to open an issue or submit a pull request if you have ideas for improvement.

## License

This project is licensed under the [[Apache LICENSE 2.0](https://www.apache.org/licenses/LICENSE-2.0)].

## Contact

For any inquiries, email me at [shivam.hireme@gmail.com](mailto:shivam.hireme@gmail.com).

## Support the Project

Help support continued development and improvements:

- **Follow on LinkedIn**: Stay connected for updates – [LinkedIn Profile](https://www.linkedin.com/in/shivam-hireme//)
- **Buy Me a Coffee**: Appreciate the project? [Buy Me a Coffee](https://buymeacoffee.com/shivamshane)