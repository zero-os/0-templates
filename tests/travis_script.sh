job_key="ZOS-ZTEMP-${TRAVIS_JOB_NUMBER}"

action=$1

if [[ ${action} == "setup" ]]; then

    echo "[+] Creating zerotier network ..."
    zerotier_network=$(python3 -u tests/utils.py -a create_zerotier_network -s ${zerotier_token}); sleep 5
    printf ${zerotier_network} > /tmp/zerotier_network.txt

    echo "[+] Joining zerotier network: ${zerotier_network}"
    sudo zerotier-cli join ${zerotier_network}; sleep 15
    memberid=$(sudo zerotier-cli info | awk '{print $3}')
    curl -s -H "Content-Type: application/json" -H "Authorization: Bearer ${zerotier_token}" -X POST -d '{"config": {"authorized": true}}' https://my.zerotier.com/api/network/${zerotier_network}/member/${memberid} > /dev/null

    echo "[+] Creating ${number_of_nodes} Zero-OS node(s) on packet.net"
    python3 tests/utils.py -a create_nodes -t ${packet_token} -b ${zero_os_branch} -k ${job_key} -z ${zerotier_network} -n ${number_of_nodes}
    
    echo "[+] Installing JumpScale9 ..."
    ./utils/jumspcale_install.sh ${js9_branch}
    
    echo "[+] Installing 0-robot"
    ./utils/zrobot_install.sh ${zrobot_branch}

    echo "[+] Starting 0-robot server ..." 
    zrobot server start -T https://github.com/zero-os/0-templates.git -D https://github.com/ahmedelsayed-93/data-repo &> /tmp/zrobot.log &

    sleep 10

    cat /tmp/zrobot.log

    echo "[+] Connecting to the 0-robot server ..."
    zrobot robot connect main http://localhost:6600

    echo "[+] Start bootstrap service ..."
    python3 -u tests/utils.py -a bootstrap -z ${zerotier_network} -s ${zerotier_token} -n ${number_of_nodes}

elif [[ ${action} == "test" ]]; then

    echo "[+] Running tests ..."
    zrobot service list    

elif [[ ${action} == "teardown" ]]; then

    echo "[+] Deleting Zero-OS node(s) ..."
    python3 tests/utils.py -a delete_nodes -t ${packet_token} -k ${job_key}

fi