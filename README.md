# Project Documentation: Slack Bot for AMAT Project

## Table of Contents
1. [Introduction](#introduction)
2. [Setup](#setup)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
3. [Usage](#usage)
   - [Starting the Application](#starting-the-application)
   - [Stopping the Application](#stopping-the-application)
   - [Database Management](#database-management)
4. [Project Structure](#project-structure)
5. [Slack Bot Usage](#slack-bot-usage)
6. [Additional Information](#additional-information)

## Introduction
This document outlines the setup and usage of the Slack bot developed for the AMAT project. The bot is designed to assist with various tasks within a Slack workspace.

## Setup

### Prerequisites
- Git
- Docker
- Make
- Python 3.12.4

### Installation
1. Clone the repository:
   ```
   git clone <repository_url>
   cd <repository_directory>
   ```

2. Set up the environment:
   ```
   make up
   ```

## Usage

### Starting the Application
To launch the Docker containers:
```
make up
```
Note: Set the `DATABASE_URL` environment variable to `db` before starting.

### Stopping the Application
To stop and remove Docker containers:
```
make down
```

### Database Management
For database migrations:
1. Create a new revision:
   ```
   make revision
   ```
2. Apply the migration:
   ```
   make migrate
   ```
Note: Change `DATABASE_URL` to `localhost` for migrations after containers are running.

## Project Structure
- `Makefile`: Contains project management commands
- `poetry`: Dependency management
- `desktop_dispatcher/`:
  - `events`: Slack bot event handlers
  - `main`: Application entry point
  - `session`: Database session management
  - `utils`: Utility functions
  - `modeles`: Application models
- `bot_deployment/`: K8s and HELM deployment config
- `Dockerfile`: docker instructions 

## Slack Bot Usage
1. Add the bot to your Slack workspace
2. Send a direct message to the bot:
   ```
   /desktop
   ```
3. Follow the prompts to manage your desktop environment

## Additional Information
- Project ideas are in the `notes` file
- Refer to the Makefile for all available commands
