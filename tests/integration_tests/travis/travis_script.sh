
install_jumpscale(){
    js9_branch=${js9_branch:-"development"}

    ## install important packages
    apt install git python3-pip python-pip -y
    apt install python-dev python3-dev libffi-dev build-essential libssl-dev libxml2-dev libxslt1-dev zlib1g-dev -y
    
    ## install jumpscale 
    for target in /usr/local /opt /opt/cfg /opt/code/github/jumpscale /opt/var/capnp /opt/var/log $HOME/js9host/cfg; do
        mkdir -p $target
        sudo chown -R $USER:$USER $target
    done

    for target in core9 lib9 prefab9; do
        git clone --depth=1 -b ${js9_branch} https://github.com/jumpscale/${target} /opt/code/github/jumpscale/${target}
        pip3 install -e /opt/code/github/jumpscale/${target}
    done
}

initialize_js_config_manager(){
    path=${1:-"/opt/code/config_manager"}
    mkdir -p ${path}
    git init ${path}
    touch ${path}/.jsconfig
    js9_config init --silent --path ${path}/ --key ~/.ssh/id_rsa
}

install_zrobot(){
    sudo apt-get install -y libsqlite3-dev
    mkdir -p /opt/code/github/zero-os
    cd /opt/code/github/zero-os
    git clone https://github.com/zero-os/0-robot.git
    cd 0-robot
    pip install -e .
}

join_zerotier_network(){
    echo "[+] Joining zerotier network: ${1}"
    sudo zerotier-cli join ${1}; sleep 5
    memberid=$(sudo zerotier-cli info | awk '{print $3}')
    curl -s -H "Content-Type: application/json" -H "Authorization: Bearer ${2}" -X POST -d '{"config": {"authorized": true}}' https://my.zerotier.com/api/network/${1}/member/${memberid} > /dev/null
    sudo ifconfig "$(ls /sys/class/net | grep zt)" mtu 1280 
}


echo "[+] Generating ssh key ..."
ssh-keygen -f ~/.ssh/id_rsa -P ''

echo "[+] Joining router zerotier network"
join_zerotier_network ${zerotier_network} ${zerotier_token}

echo "[+] Installing JumpScale9 ..."
install_jumpscale

echo "[+]  Initializing JumpScale9 config manager ..."
initialize_js_config_manager

echo "[+] Installing 0-robot ..."
install_zrobot

echo "[+] Setting up testing environment ..."
python3 -u tests/integration_tests/travis/zboot_env_setup.py --router_address ${router_address} --router_username ${router_username} --router_password ${router_password} --zerotier_network ${zerotier_network} --zerotier_token ${zerotier_token} --rack_hostname ${rack_hostname} --rack_username ${rack_username} --rack_password ${rack_password} --rack_module_id ${rack_module_id} --cpu_hostname ${cpu_hostname} --cpu_rack_port ${cpu_rack_port} --core_0_branch ${core_0_branch}

echo "[+] Joining testing zerotier network"
testing_zt_network=$(cat /tmp/testing_zt_network.txt)
join_zerotier_network ${testing_zt_network} ${zerotier_token}

echo "[+] Preparing testing framework ..."
bash tests/integration_tests/prepare.sh

echo "[+] Installing tests requirements ..."
bash pip3 install -r tests/integration_tests/requirements.txt

echo "[+] Running tests ..."
cd /tests/integration_tests 
cpu_zt_ip=$(cat /tmp/cpu_zt_ip.txt)
nosetests -v -s testsuite --tc-file=config.ini --tc=main.redisaddr:${cpu_zt_ip}