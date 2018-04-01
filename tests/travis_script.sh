job_key="${TRAVIS_JOB_NUMBER}"

action=$1

if [[ ${action} == "setup" ]]; then

    echo "[+] Generating ssh key ..."
    ssh-keygen -f ~/.ssh/id_rsa -P ''

    echo "[+] Creating zerotier network"
    zerotier_network=$(python3 -u tests/utils.py -a create_zerotier_network -s ${zerotier_token}); sleep 5

    echo "[+] Creating ctrl ..."
    python3 -u tests/utils.py -a create_ctrl -t ${packet_token} -k ${job_key}

    echo "[+] Creating ${number_of_nodes} Zero-OS node(s) on packet.net"
    python3 -u tests/utils.py -a create_nodes -t ${packet_token} -b ${zero_os_branch} -k ${job_key} -z ${zerotier_network} -n ${number_of_nodes}

elif [[ ${action} == "test" ]]; then

    zerotier_network=$(cat /tmp/zerotier_network.txt)
    ctrl_ipaddress=$(cat /tmp/device_ipaddress.txt)
    scp -o StrictHostKeyChecking=no tests/setup.sh root@${ctrl_ipaddress}:/root/
    ssh -t -o StrictHostKeyChecking=no root@${ctrl_ipaddress} "bash setup.sh ${zero_templates_branch} ${js9_branch} ${zrobot_branch} ${zerotier_network} ${zerotier_token} ${number_of_nodes}"   

fi