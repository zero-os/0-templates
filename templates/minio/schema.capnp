@0x9895a7c4a0b2bd61; 


struct Schema {
    node @0: Text; # name of the node service to where minio will be deployed
    zerodbs @1: List(Text); # names of the 0-db services used as backend for minio
    namespace @2: Text; # namespace to use on the 0-db
    nsSecret @3: Text; # secret to use to have access to the namespace on the 0-db servers
    login @4: Text; # minio login. End user needs to know this login to have access to minio
    password @5: Text; #minio password. End user needs to know this login to have access to minio
    container @6: Text; # reference to the container on which minio will be running. This is set by the template
    listenPort @7: UInt32=9000; # the port to bind to
    resticRepo @8: Text="s3:http://195.134.212.42/"; # restic repo to use for metadata backup
    resticUsername @9: Text="zaibon"; # rustic username
    resticPassword @10: Text="coucou01"; # rustic password
    privateKey @11: Text; # encryption private key
}