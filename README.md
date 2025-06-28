# 🐾 Paw & Order: An AI-Powered Web Application

Welcome to **Paw & Order**. This project has been structured as a modern web application with a Python backend and an HTML/CSS/JavaScript frontend.

## Table of Contents
1.  [How to Run the Game](#how-to-run-the-game)
2.  [Project Structure](#project-structure)
3.  [File Descriptions](#file-descriptions)
4.  [Architecture Overview](#architecture-overview)
5.  [Technologies Used](#technologies-used)

---

## How to Run the Game

This project requires a running Python server.

### Prerequisites
* Python 3.x installed on your system.
* `pip` (Python's package installer).

### 1. Installation
Open your terminal or command prompt and install the required Python library, Flask:
```bash
pip install Flask
```

### 2. Set Up the Project
1.  Create a main folder for the project (e.g., `paw-and-order`).
2.  Save `app.py` inside this main folder.
3.  Create a subfolder named `templates` and save `index.html` inside it.
4.  Create another subfolder named `static` and save `style.css` and `script.js` inside it.

### 3. Run the Server
1.  Navigate to the main project folder (`paw-and-order`) in your terminal.
2.  Run the following command to start the Flask server:
    ```bash
    python app.py
    ```
3.  You will see output indicating the server is running, usually on `http://127.0.0.1:5001`.

### 4. Play the Game
Open your web browser and navigate to the address from the previous step: **`http://127.0.0.1:5001`**. The game will load, and you can begin playing.

---

## Project Structure

The project is organized into a standard client-server structure:

```
paw-and-order-app/
├── app.py              (Python Backend Server)
│
├── templates/
│   └── index.html      (HTML Frontend Structure)
│
├── static/
│   ├── style.css       (CSS Styling)
│   └── script.js       (JavaScript Frontend Logic)
│
└── report/
    └── report.tex      (LaTeX Project Report Source)
```

---

## File Descriptions

### `app.py`
This is the **backend** of the application. It's a Python script that uses the Flask framework to create a web server. Its responsibilities include:
* Serving the `index.html` file to the user's browser.
* Handling all game logic (managing turns, state, etc.).
* Running the AI calculations for both the Minimax Im-paw-ster and the Naive Bayes Detective.
* Providing API endpoints (`/api/start`, `/api/action`) that the frontend can communicate with.

### `templates/index.html`
This is the main **HTML template** for the user interface. It defines the structure of the game screens but does not contain any game logic itself. It links to the CSS and JavaScript files.

### `static/style.css`
This file contains all the **CSS rules** for the game's visual presentation, including layout, colors, fonts, and animations.

### `static/script.js`
This file is the **frontend logic**. Its role has changed significantly from the previous version. It does *not* contain any game rules or AI. Its sole responsibilities are:
* Sending the player's actions (like choosing a location or voting) to the Python backend.
* Receiving the updated game state from the backend after a turn is processed.
* Rendering the received game state to the user by dynamically updating the HTML.

### `report/report.tex`
This file contains the LaTeX source code for the formal project report. It details the project's problem statement, technical approach, software architecture, evaluation, and conclusions.

---

## Architecture Overview

This application uses a **client-server model**:

1.  The **Server** (`app.py`) runs on a machine and holds the true state of the game.
2.  The **Client** (the user's web browser) loads the HTML, CSS, and JS files to display the user interface.
3.  When a player takes an action, the client's JavaScript sends a request to the server's API.
4.  The server processes the action, runs the AI's turn, updates the game state, and sends the new state back to the client.
5.  The client's JavaScript receives the new state and updates the page to reflect the changes.

---

## Technologies Used

* **Backend:** Python, Flask
* **Frontend:** HTML5, CSS3, JavaScript (ES6)
