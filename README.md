# Blog GotIt Backend Test

## Table of Contents

- [Installation](#installation)
- [API Documentation](#api-documentation)
- [A Note on Facebook/Google Authentication](#a-note-on-facebookgoogle-authentication)

## Installation

### This application requires `Python 3.9.7`, `Docker`, and `docker-compose` to run.

```sh
cd blog-gotit
```

### Set up

Inside `docker-compose.yml`, under `db` service, you could change `MYSQL_USER` and `MYSQL_PASSWORD` to your own ones or leave it as default.

Create a file named `.env` in your root directory with this structure.

```
SECRET_KEY=<YOUR_SECRET_KEY>
JWT_SECRET_KEY=<YOUR_JWT_SECRET_KEY>
DATABASE_URL=mysql+pymysql://<MYSQL_USER>:<MYSQL_PASSWORD>@db/blog_gotit
FIREBASE_SDK_KEY=keys/<YOUR_FIREBASE_SDK_CREDENTIALS>
MAIL_SERVER=smtp.googlemail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=<YOUR_EMAIL_USERNAME>
MAIL_PASSWORD=<YOUR_PASSWORD>
ADMINS=<LIST_OF_EMAILS_SEPARATED_BY_COMMAS>
```

To get `<YOUR_FIREBASE_SDK_CREDENTIALS>` for Google Authentication

1.  Go to [https://firebase.google.com/](https://firebase.google.com/)
2.  Click **Go to console**.
3.  Create a project
    - **Add project**/**Create project**.
    - Enter your project name.
    - Unselect **Enable Google Analytics for this project**.
    - Click **Save**.
4.  Enable Google Authentication
    - From the sidebar, click **Authentication**.
    - Under **Sign-in method** tab, click **Google**.
    - Click **Enable**
    - Click **Save**.
5.  Download Python Firebase Admin SDK
    - Go to **Project settings** from the sidebar.
    - Under **Service accounts** tab, choose `Python` for your Admin SDK.
    - Click **Generate new private key**.
    - Store the downloaded file in `keys` folder.
6.  Finally, in `.env`, replace `<YOUR_FIREBASE_SDK_CREDENTIALS>` with the downloaded file's name.
    - (e.g. `FIREBASE_SDK_KEY=keys/blog-gotit-firebase-adminsdk-***.json`)

A complete example

```
SECRET_KEY=123456
JWT_SECRET_KEY=123456
DATABASE_URL=mysql+pymysql://interview:interview@db/blog_gotit
FIREBASE_SDK_KEY=keys/blog-gotit-firebase-adminsdk-***.json
MAIL_SERVER=smtp.googlemail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=example
MAIL_PASSWORD=example
ADMINS=example1@mail.com,example2@mail.com
```

### Deployment

In the root directory, run

```sh
docker-compose up --build
```

It takes 5 minutes or more to complete.

When finished, you should see

```sh
...
... INFO in __init__: Server Startup
...
... 0 [System] [MY-010931] [Server] /usr/sbin/mysqld: ready for connections. Version: '8.0.26'  socket: '/var/run/mysqld/mysqld.sock'  port: 3306  MySQL Community Server - GPL.
```

which means your build has successfully completed.

## API Documentation

To access the documentation, go to [http://localhost:8000/apidocs](http://localhost:8000/apidocs) when the server is up.

## A Note on Facebook/Google Authentication

On the CLIENT:

1. Use the Facebook API/Firebase Google Authentication to login and get an OAUTH2 code.
2. Exchange this code for an access token.
3. Request an access token from my SERVER, including the Facebook/Google access token as a parameter

On the SERVER

1. Receive access token request.
2. Make a request to the /me Facebook graph using Facebook access token or call `verify_id_token(access_token)` in Firebase Admin SDK using Google access token
3. Verify that the Facebook/Google user exists and match to a user in my database
4. Create my own access token, save it and return it to the client to be used from this point forward
