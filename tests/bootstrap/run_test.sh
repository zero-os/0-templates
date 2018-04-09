zerotier_network=$(cat /tmp/zerotier_network.txt)
ctrl_ipaddress=$(cat /tmp/device_ipaddress.txt)
scp -o StrictHostKeyChecking=no tests/bootstrap/test.sh root@${ctrl_ipaddress}:/root/
scp -o StrictHostKeyChecking=no tests/utils.sh root@${ctrl_ipaddress}:/root/
scp -o StrictHostKeyChecking=no tests/utils.py root@${ctrl_ipaddress}:/root/
ssh -t -o StrictHostKeyChecking=no root@${ctrl_ipaddress} "bash test.sh ${js9_branch} ${zrobot_branch} ${zerotier_network} ${zerotier_token} ${number_of_nodes}"