export LANGUAGE=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_TYPE=en_US.UTF-8

zero_templates_branch=${1} 
js9_branch=${2}
zrobot_branch=${3}
zerotier_network=${4}
zerotier_token=${5}
number_of_nodes=${6}

echo "[+] Installing requirements"
apt update
#install python packages
apt install git python3-pip python-pip -y
apt install python-dev python3-dev libffi-dev build-essential libssl-dev libxml2-dev libxslt1-dev zlib1g-dev -y
pip3 install python-dateutil requests zerotier git+https://github.com/gigforks/packet-python.git
# install zerotier
curl -s https://install.zerotier.com/ | sudo bash

echo "[+] Joining zerotier network: ${zerotier_network}"
sudo zerotier-cli join ${zerotier_network}; sleep 10
memberid=$(sudo zerotier-cli info | awk '{print $3}')
curl -s -H "Content-Type: application/json" -H "Authorization: Bearer ${zerotier_token}" -X POST -d '{"config": {"authorized": true}}' https://my.zerotier.com/api/network/${zerotier_network}/member/${memberid} > /dev/null

echo "[+] Cloning 0-template repo"
git clone -b ${zero_templates_branch:-master} https://github.com/zero-os/0-templates

echo "[+] Installing Jumpscale9"
0-templates/utils/jumspcale_install.sh ${js9_branch}

echo "[+] Installing 0-robot"
0-templates/utils/zrobot_install.sh ${zrobot_branch}

echo "[+] Stating 0-robot server"
zrobot server start -T https://github.com/zero-os/0-templates.git -D https://github.com/ahmedelsayed-93/data-repo &> /tmp/zrobot.log &
sleep 30
zrobot robot connect main http://localhost:6600

echo "[+] Start bootstrap service"
python3 -u 0-templates/tests/utils.py -a bootstrap -z ${zerotier_network} -s ${zerotier_token} -n ${number_of_nodes}