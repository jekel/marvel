**Setup**

Configure KEY and SECRET env variables in Dockerfile

**Run and test**

docker build -t marvel . && docker run -p 5000:8080 marvel

curl http://0.0.0.0:5000/3-D%20Man