echo "[+] Connecting to 0-robot server ..."
cpu_zt_ip=$(cat /tmp/ip.txt)
zrobot robot connect main http://${cpu_zt_ip}:6600
sleep 20

echo "[+] Running tests ..."
nosetests -v -s ${tests_path} --tc-file=config.ini --tc=main.redisaddr:${cpu_zt_ip}
