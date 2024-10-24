# Technical Overview

## Overview

**RAVEN** is an open source web based Air Quality data validation and e-reporting system, with the aim to control the flow, metadata inventory, the quality of the monitoring data and producing the XML files required for the Air Quality B-G, except from D1b (Information on the assessment methods - for models and objective estimation) and E1b (Information on primary validated assessment data – modelled).  
The system is managed and developed by `NILU`, with support from `4sFera`, on the behalf of the `European Environmental Agency`.

## Technologies Used

### Backend

- **Python 3.10.9**: Provides the core backend logic using modern Python capabilities.
  - **Flask**: Lightweight WSGI web application framework used for building the API layer.
  - **Gunicorn**: Python WSGI HTTP server used to serve the Flask application in production.
  - **Pandas**: Library for data manipulation and analysis.
- **PostgreSQL 12+**: Relational database management system, ensuring data consistency and reliability.
- **PostGIS Extension**: Adds support for geographic objects in PostgreSQL, enabling spatial queries and GIS functionality.

### Frontend

- **Node.js 18.12.1**: Used primarily to manage frontend package installation and build processes.
- **Vue.js**: Frontend JavaScript framework for building reactive and dynamic user interfaces.
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development with a mobile-first design approach.
- **Vite.js**: Next-generation frontend tooling for faster and leaner development, serving as a build tool.

### Deployment

- **Docker**: Containerization tool used to package the application for a consistent and portable environment.
- **Nginx**: Web server used as a reverse proxy. It directs incomming request to client or api based on the request path.

## Database Architecture

![Raven DB Architecture](./assets/ravendb.png)

_Click to to enlarge image_

## Installation

1. Clone the repository:

   ```bash
   git clone https://git.nilu.no/raven/raven-administration.git
   ```

2. Create the `.env` file

3. Build and run with Docker:

   ```bash
   docker-compose up --build
   ```

4. Access the application via `http://localhost`.

## License

Raven is licensed under the **GNU GPLv3** license.
