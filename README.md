# digest
Just a simple messages digest service used to calculate, store and retrive `sha256` of string messages

## Deploying

Either:
1. Pull the ready image using `docker pull shayweiss/simple-digest` or
2. Clone this repo and run `docker build -t shayweiss/simple-digest .`

## Running
Just run the `launch.sh` script in the root of this repo

## Usage
The following is written assuming you are on the running container.
This can be achieved by running `docker exec -i -t digest /bin/bash`

### Sanity Check
You can make sure your service is running with `curl http://localhost:5000/ping`

e.g:
```
root@6cdba16398d6:/digest-flask-web-app# curl http://localhost:5000/ping
{"message": "All is well!"}
root@6cdba16398d6:/digest-flask-web-app# 
```

### store a message
Hit the `/messages` endpoint with an HTTP `POST` request, `Content-Type: application/json` header and a `JSON` payload in the form of: `{"message": <SOME_STRING_MESSAGE>}`

#### Example
```root@6cdba16398d6:/digest-flask-web-app# curl -XPOST -H "Content-Type: application/json" http://localhost:5000/messages -d '{"message": "foo"}'```

You will recieve a response with `200` status code and a `JSON` containing the `sha256` of your stiring, e.g:
```{"message": "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"}```

### Retrieve a previously stored message
Hit the `/messages/<sha256>` endpoint with an HTTP `GET` request.

#### Example
```root@6cdba16398d6:/digest-flask-web-app# curl http://localhost:5000/messages/2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae```

You will recieve a response with `200` status code and a `JSON` containing the original stiring, e.g:
```{"message": "foo"}```

### "database"
The "database" is a persistent `JSON` file on the container, located at: `/digest-flask-web-app/app.db`

### Logs
The logs for the service are located at: `/digest-flask-web-app/app.log`.  
They are rotated every 1000000 bytes and up to 5 files are kept.  
This is configurable in `digest.py`
