sudo mkdir -p /mnt/nlpa
sudo chown "$USER":"$USER" /mnt/nlpa
sshfs timparkin@192.168.64.1:/Volumes/NLPASCRATCH /mnt/nlpa \
  -o reconnect \
  -o idmap=user \
  -o uid=$(id -u) -o gid=$(id -g) \
  -o umask=022
