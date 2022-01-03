#!/bin/bash

cont (){
        read -p "Continue? (y/n): " -n 1 -r
        echo    # (optional) move to a new line
        if [[ $REPLY =~ ^[Yy]$ ]]; then
                return
        else
                false
        fi
}

pushd /etc/systemd/system
sudo cp picofanpwm.service /etc/systemd/system
sudo systemctl enable picofanpwm.service
popd

sudo ln -s $(pwd)/tempsend.py /usr/local/bin
echo "Fake GPU? (developing on a laptop?)"
cont && sudo ln -s $(pwd)/fake-gpu.sh /usr/local/bin/nvidia-smi

echo "Reset settings to defaults?"
cont && cp fansettings.defaults.py fansettings.py

echo "Start service?"
cont && sudo systemctl start picofanpwm