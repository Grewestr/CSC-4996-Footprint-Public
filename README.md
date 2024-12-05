# Footprint Web Application - README

Welcome to the **Footprint Web Application** repository! This document provides comprehensive instructions for setting up, running, and testing the Footprint application in your local environment. Follow these steps to ensure proper functionality. Most of the important code is either in views.py for the website or AI_Scripts folder for the AI models.

---

## **Table of Contents**
1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Setup Instructions](#setup-instructions)
4. [Modifying Absolute Paths](#modifying-absolute-paths)
5. [Running the Application](#running-the-application)
6. [Testing Environment](#testing-environment)
7. [Troubleshooting](#troubleshooting)
8. [Contributing](#contributing)
9. [License](#license)

---

## **Overview**

The **Footprint Web Application** is a web-based tool designed to help law enforcement locate missing persons using clothing attribute detection from video feeds. This application leverages advanced machine learning models and is deployed locally on a Windows 11 laptop.

---

## **System Requirements**

### **Hardware**
- **Operating System**: Windows 11 (64-bit)
- **Processor**: 2.0 GHz dual-core or higher
- **Memory**: 8 GB RAM (minimum)
- **Storage**: 10 GB of free disk space

### **Software**
- **Docker Desktop**: Latest version
- **Python**: Version 3.9 or later
- **Git**: Version control system
- **Web Browsers**: Google Chrome, Microsoft Edge, Firefox, or Safari (latest versions)

### **Network**
- A stable internet connection is required.

---

## **Setup Instructions**

### Step 1: Clone the Repository
1. Open a terminal on your Windows 11 laptop.
2. Clone the **Integration** branch of the GitHub repository:
   ```bash
   git clone --branch Integration https://github.com/<your-repository-url>.git
   cd <repository-directory>
   ```

### Step 2: Create a Virtual Environment
1. Create a virtual environment in the project directory:
   ```bash
   python -m venv venv
   ```
2. Activate the virtual environment:
   - **Command Prompt**:
     ```bash
     venv\Scripts\activate
     ```
   - **PowerShell**:
     ```bash
     .\venv\Scripts\Activate.ps1
     ```

### Step 3: Install Dependencies
1. Install the dependencies listed in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

### Step 4: Build the Docker Container
1. Navigate to the `footprint` directory:
   ```bash
   cd footprint
   ```
2. Build the Docker container:
   ```bash
   docker-compose up
   ```

---

## **Modifying Absolute Paths**

### Step 1: Locate the `views.py` File
1. Navigate to the `CSC-4996-Footprint/footprint/home` directory.
2. Open the `views.py` file in a code editor.

### Step 2: Update Absolute Paths
You must change two absolute paths to match your local setup:

1. **Path 1**: In the `check_and_run_boot_commands` function, find and replace the following:
   ```python
   boot_directory = R"C:\Users\17344\Documents\Capstone2\CSC-4996-Footprint\footprint"
   ```
   Replace it with the local path to the `footprint` directory on your machine.

2. **Path 2**: In the `upload` view, find and replace the following:
   ```python
   script_directory = R"C:\Users\17344\Documents\Capstone2\CSC-4996-Footprint\footprint\home\static\AI_Scripts"
   ```
   Replace it with the local path to the `AI_Scripts` directory within the `footprint/home/static` folder.

### Step 3: Save Changes
Save the `views.py` file after modifying these paths.

---

## **Running the Application**

### Step 1: Build and Start Docker
1. In the terminal, navigate to the `footprint` directory:
   ```bash
   cd footprint
   ```
2. Run the following commands in sequence:
   ```bash
   docker-compose build
   docker-compose up
   ```

### Step 2: Start the Django Server
1. Open another terminal in the `footprint` directory.
2. Run the Django development server:
   ```bash
   python manage.py runserver
   ```
3. Access the application via `http://127.0.0.1:8000` in your web browser.

---

## **Testing Environment**

- **Device**: Windows 11 laptop with Docker Desktop installed.
- **Network**: Stable internet connection.
- **Browsers**: Test on Google Chrome, Microsoft Edge, Firefox, or Safari (latest versions).

### Recommended Tests
1. Verify the application UI renders correctly across all supported browsers.
2. Upload videos at different processing speeds (slow, medium, fast).
3. Check real-time updates in the upload queue and AI dashboard.
4. Ensure database interactions (Firestore) work as expected.

---

## **Troubleshooting**

### Common Issues
1. **Docker Build/Run Errors**:
   - Ensure Docker Desktop is running before executing the commands.
   - Verify the `docker-compose.yml` file is correctly configured.

2. **Path Errors**:
   - Double-check the absolute paths updated in `views.py`.

3. **Server Not Starting**:
   - Ensure the virtual environment is activated before running the server.

### Logs and Debugging
- Check Docker and Django logs for detailed error messages:
  ```bash
  docker-compose logs
  python manage.py runserver
  ```

---

## **Contributing**

We welcome contributions to improve the Footprint Web Application. To contribute:
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make changes and commit them:
   ```bash
   git commit -m "Describe your changes"
   ```
4. Push changes and create a pull request.

---

## **License**

This project is licensed under the [MIT License](LICENSE). Use, modify, and distribute the application as per the license terms.

---

Enjoy using the Footprint Web Application! For any questions or support, please contact [gp0569@wayne.edu].
