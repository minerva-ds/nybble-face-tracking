sudo rfcomm unbind rfcomm0
sudo rfcomm bind rfcomm0 56:76:87:07:24:16 1
sudo chmod 777 /dev/rfcomm0
#sudo minicom -w -D /dev/rfcomm0
