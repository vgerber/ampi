cd ..
sudo docker build -t fastapi-app .
sudo docker run -p 8000:80 fastapi-app