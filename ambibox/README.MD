Install python libraries on the raspbery pi :
```
sudo apt update
sudo apt install -y python3-pip python3-dev python3-rpi.gpio python3-pil python3-requests python3-spidev python3-numpy

# websocket-client n'est pas (encore) empaquete pour apt sur Raspberry Pi OS,
# d'ou l'installation via pip pour cette lib uniquement.
pip3 install websocket-client --break-system-packages
sudo pip3 install websocket-client --break-system-packages
```
Les deux lignes sont nécessaires : le script tourne en root (service systemd),
qui a son propre environnement de paquets Python distinct de l'utilisateur
courant. Sans le `sudo pip3 install`, `import websocket` echoue au demarrage
et le script plante silencieusement (le webserver ne repond jamais).

Remove hyperhdr@pi service if needed and enable hyperhdr@root service
```
sudo systemctl disable hyperhdr@pi.service
sudo systemctl enable hyperhdr@root.service
```