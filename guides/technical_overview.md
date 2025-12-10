# Technical Overview

## Overview

**RAVEN** is an open source web based Air Quality data validation and e-reporting system, with the aim to control the flow, metadata inventory, the quality of the monitoring data and producing the XML files required for the Air Quality B-G, except from D1b (Information on the assessment methods - for models and objective estimation) and E1b (Information on primary validated assessment data – modelled).  
The system is managed and developed by `NILU`, with support from `4sFera`, on the behalf of the `European Environmental Agency`.

## Technologies Used

### Backend

- **Python 3.10.9**: Core programming language.
- **Web Framework**:
  - **Flask**: Micro-framework for the API.
  - **Flask Extensions**:
    - `Flask-JWT-Extended`: JWT based authentication.
    - `Flask-Cors`: Handling Cross Origin Resource Sharing (CORS).
    - `Flask-Compress`: Response compression.
    - `Flask-HTTPAuth`: Basic HTTP authentication.
- **Data Processing & Analysis**:
  - **Pandas** & **NumPy**: Data manipulation and numerical analysis.
  - **GeoPandas**: Spatial data operations.
  - **Pydantic**: Data validation and settings management.
- **Database Interaction**:
  - **Psycopg2**: PostgreSQL adapter for Python.
- **Utilities**:
  - `python-simplexml`: XML parsing/generation.
  - `requests`: HTTP library.
  - `python-dotenv`: Environment variable management.

### Frontend

- **Core Framework**:
  - **Vue.js 3**: Progressive JavaScript framework.
  - **Vue Router**: Official router for Vue.js.
- **Build Tooling**:
  - **Vite**: Next generation frontend tooling.
  - **Node.js**: Runtime environment for build tools.
- **UI & Styling**:
  - **Tailwind CSS**: Utility-first CSS framework.
  - **Ag-Grid Vue**: Advanced data grid for displaying complex datasets.
  - **CodeMirror**: In-browser code editor.
- **Visualization**:
  - **Chart.js**: Simple yet flexible JavaScript charting.
  - **Leaflet** (`@vue-leaflet/vue-leaflet`): Interactive maps.
- **Utilities**:
  - **Axios**: Promise based HTTP client.
  - **Luxon** & **Date-fns**: Date and time manipulation.
  - **VueUse**: Collection of essential Vue Composition Utilities.
  - **Mitt**: Tiny functional event emitter.

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
