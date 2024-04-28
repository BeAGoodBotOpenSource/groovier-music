## Ideas

For now, we will use one account and its associated client id and secret to interface with all users. This means that all new playlists will be created under this one account. This has the benefit of users not needing to go through a OAuth process, but we should eventually change this to something more secure. For now, it serves the purpose.	

## Setup

This application is containerized using Docker. To run the application, you need to have Docker installed on your machine. If you don't have Docker installed, you can download it from here: https://www.docker.com/products/docker-desktop.

Same as frontend, create a ".env" file and add the following secrets with their values, of course: 
```bash
CLIENT_ID=
CLIENT_SECRET=
REDIRECT_URI=http://localhost:5001
OPENAI_API_KEY=
ORGANIZATION_ID=
SPOTIFY_USERNAME=barista85
```

## Building the docker image

To build the Docker image for the application, navigate to the project directory and run (including the . at the end):

```bash
docker build -t groovy-music-app .
```
This command will pull the Python base image, install all necessary packages from the 'requirements.txt' file, and set up the application to be run by Gunicorn.

# Running the Docker container

Once the Docker image has been built, you can start the container by running:

```bash
docker run -p 4000:80 groovy-music-app
```

This command will start the Docker container and bind port 80 inside the container (where our application is running) to port 4000 on your machine. You can then access the application at http://localhost:4000.

## Contributing

When adding new Python packages, please remember to update the requirements.txt file. This file is used by Docker to install necessary dependencies. To update the requirements.txt file, please run:

```bash
pip freeze > requirements.txt
```
This command should be run from within the virtual environment to capture the correct list of packages.

## Quickstart

If you prefer to start the python server without Docker, you can do so by running:

```bash
python server.py
```
Please note that this method may not mirror the production environment closely, and it's recommended to use Docker for a more accurate testing environment.
