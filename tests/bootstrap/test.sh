source utils.sh

js9_branch=${1}
zrobot_branch=${2}
zerotier_network=${3}
zerotier_token=${4}
number_of_nodes=${5}

# installing requirements
apt update
apt install git python3-pip python-pip -y
pip3 install python-dateutil requests zerotier git+https://github.com/gigforks/packet-python.git

# install zerotier
install_zerotier

# join zerotier netowork
join_zerotier_network ${zerotier_network} ${zerotier_token}

# install jumpscale
install_jumpscale ${js9_branch}

# install 0-robot
install_zrobot ${zrobot_branch}

# start 0-robot server
zrobot server start -T https://github.com/zero-os/0-templates.git -D https://github.com/ahmedelsayed-93/data-repo &> /tmp/zrobot.log &

# wait for 0-robot server to start
sleep 30

# connect to 0-robot
zrobot robot connect main http://localhost:6600

# run bootstrap service
python3 -u utils.py -a bootstrap -z ${zerotier_network} -s ${zerotier_token} -n ${number_of_nodes}