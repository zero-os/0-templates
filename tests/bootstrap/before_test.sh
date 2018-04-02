job_key="${TRAVIS_JOB_NUMBER}"

echo "[+] Generating ssh key ..."
ssh-keygen -f ~/.ssh/id_rsa -P ''

echo "[+] Creating zerotier network"
zerotier_network=$(python3 -u tests/utils.py -a create_zerotier_network -s ${zerotier_token}); sleep 5

echo "[+] Creating ctrl ..."
python3 -u tests/utils.py -a create_ctrl -t ${packet_token} -k ${job_key}

echo "[+] Creating ${number_of_nodes} Zero-OS node(s) on packet.net"
python3 -u tests/utils.py -a create_nodes -t ${packet_token} -b ${zero_os_branch} -k ${job_key} -z ${zerotier_network} -n ${number_of_nodes}
