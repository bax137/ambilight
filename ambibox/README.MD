Install python libraries on the raspbery pi :
```
sudo apt install python3-pip
sudo apt install python3-dev
sudo apt install python3-rpi.gpio
sudo apt install python3-pil
sudo apt install python3-requests
python3-requests
pip3 install websocket-client
pip3 install spidev

```

Remove hyperhdr@pi service if needed and enable hyperhdr@root service
```
sudo systemctl disable hyperhdr@pi.service
sudo systemctl enable hyperhdr@root.service
```