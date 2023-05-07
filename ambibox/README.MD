Install python libraries on the raspbery pi :
```
sudo apt install python3-pip
pip3 install websocket-client
pip3 install spidev
sudo pip3 install websocket-client
sudo pip3 install spidev
```

Remove hyperhdr@pi service if needed and enable hyperhdr@root service
```
sudo systemctl disable hyperhdr@pi.service
sudo systemctl enable hyperhdr@root.service
```