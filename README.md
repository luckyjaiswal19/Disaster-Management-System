# Disaster Management & Relief Coordination System

A centralized disaster relief coordination platform featuring interactive event mapping with Leaflet, real-time resource inventory tracking, and streamlined request workflows. Enables efficient crisis response through role-based volunteer management, secure donation handling, and rapid administrative approval systems.

## Features

- **Interactive Disaster Map**: Visualize active disaster events and their severity on a dynamic map using Leaflet.js.
- **Resource Management**: real-time tracking of relief resources (food, medical supplies, shelter) including available quantities and categories.
- **Donation System**: Secure workflow for users to donate specific resources to relief efforts or specific events.
- **Request Coordination**: Streamlined process for affected individuals to request aid, with an administrative approval workflow.
- **Role-Based Dashboards**:
  - **Admin**: Manage events, resources, approve requests, and oversee volunteer assignments.
  - **User**: View active events, make donations, and request resources.
  - **Volunteer**: View assignments and update status.
- **Volunteer Coordination**: Assign volunteers to specific requests and track completion status.

## Tech Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Database**: SQLite
- **Frontend**: HTML5, Bootstrap 5, Jinja2 Templates
- **Mapping**: Leaflet.js, OpenStreetMap

## Installation

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd "Disaster Management & Relief Coordination System"
    ```

2.  **Set up a virtual environment**
    ```bash
    cd backend
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the database**
    The application uses SQLite. Ensure the database is initialized (usually handled on app startup or via a script).

## Usage

1.  **Run the application**
    ```bash
    python app.py
    ```

2.  **Access the application**
    Open your browser and navigate to `http://127.0.0.1:5000`

### Demo Accounts

- **Admin Account**:
    - Email: `admin@disaster.org`
    - Password: `password123`

- **User Account**:
    - Email: `john@example.com`
    - Password: `password123`
