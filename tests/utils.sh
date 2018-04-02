export LANGUAGE=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_TYPE=en_US.UTF-8

generate_ssh_key(){
    echo "[+] Generating ssh key ..."
    mkdir -p ~/.ssh
    ssh-keygen -f ~/.ssh/id_rsa -P ''
    eval `ssh-agent -s`
    ssh-add ~/.ssh/id_rsa
}

install_jumpscale(){
    echo "[+] Install JumpScale9 ..."
    
    BRANCH=${1:-"development"}

    ## install important packages
    apt install git python3-pip python-pip -y
    apt install python-dev python3-dev libffi-dev build-essential libssl-dev libxml2-dev libxslt1-dev zlib1g-dev -y

    ## install jumpscale 
    for target in /usr/local /opt /opt/cfg /opt/code/github/jumpscale /opt/var/capnp /opt/var/log $HOME/js9host/cfg; do
        mkdir -p $target
        sudo chown -R $USER:$USER $target
    done

    for target in core9 lib9; do
        git clone --depth=1 -b ${BRANCH} https://github.com/jumpscale/${target} /opt/code/github/jumpscale/${target}
        pip3 install -e /opt/code/github/jumpscale/${target}
    done
}

initialize_js_config_manager(){
    echo "[+] Initialize jumpscale config manager ..."
    path=${1:-"/opt/code/config_manager"}
    mkdir -p ${path}
    git init ${path}
    touch ${path}/.jsconfig
    js9_config init --silent --path ${path}/ --key ~/.ssh/id_rsa
}

install_zrobot(){
    echo "[+] Install 0-robot ..."
    BRANCH=${1:-"master"}
    mkdir -p /opt/code/github/jumpscale
    git clone --depth=1 -b ${BRANCH} https://github.com/Jumpscale/0-robot /opt/code/github/jumpscale/0-robot
    pip3 install -r /opt/code/github/jumpscale/0-robot/equirements.txt
    pip3 install /opt/code/github/jumpscale/0-robot
}


install_zerotier(){
    curl -s https://install.zerotier.com/ | sudo bash
}

join_zerotier_network(){
    zerotier_network=${1}
    zerotier_token=${2}

    echo "[+] Joining zerotier network: ${zerotier_network}"
    sudo zerotier-cli join ${zerotier_network}; sleep 5
    memberid=$(sudo zerotier-cli info | awk '{print $3}')
    curl -s -H "Content-Type: application/json" -H "Authorization: Bearer ${zerotier_token}" -X POST -d '{"config": {"authorized": true}}' https://my.zerotier.com/api/network/${zerotier_network}/member/${memberid} > /dev/null
}

delete_zerotier_network(){
    zerotier_network=${1}
    zerotier_token=${2}
    curl -s -H "Content-Type: application/json" -H "Authorization: Bearer ${zerotier_token}" -X DELETE https://my.zerotier.com/api/network/${zerotier_network}
}
