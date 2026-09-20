#!/bin/sh

DIR=`dirname $0`

cd ${DIR}

FILE=PhotoCryX.desktop

echo "[Desktop Entry]"                          >  ${FILE}
echo "Type=Application"                         >> ${FILE}
echo "Terminal=false"                           >> ${FILE}
echo "Version=1"                              >> ${FILE}
echo "Name=PhotoCryX"                               >> ${FILE}
echo "Path=${PWD}/"                          >> ${FILE}
# for UBUNTU
echo "Exec=gnome-terminal -- bash -c 'export PATH=$HOME/anaconda3/bin:\$PATH &&cd \"${PWD}\" && source activate mp && python3 code.py'" >> ${FILE}
# for KALI Linux specify the python path
#echo "Exec=qterminal -e \"bash -c 'export PATH=$HOME/anaconda3/bin:\$PATH && cd \\\"${PWD}\\\" && source activate mp && python code.py'\"" >> ${FILE}

echo "Icon=${PWD}/photocryx.png"                >> ${FILE}

chmod +x ${FILE}



