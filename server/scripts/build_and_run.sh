sudo docker build -t vgerber/ampi-server:local .
sudo docker run -e PORT=8123 --network host vgerber/ampi-server:local
