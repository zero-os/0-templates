@0x9895a7c4a0b2bd61; 


struct Schema {
    node @0: Text; # name of the node service to where minio will be deployed
    zerodbs @1: List(Text); # names of the 0-db services used as backend for minio
    namespace @2: Text; # namespace to use on the 0-db
    nsSecret @3: Text; # secret to use to have access to the namespace on the 0-db servers
    login @4: Text; # minio login. End user needs to know this login to have access to minio
    password @5: Text; #minio password. End user needs to know this login to have access to minio
    container @6: Text; # reference to the container on which minio will be running. This is set by the template
    listenAddr @7: Text="0.0.0.0"; # the address to bind to
    listenPort @8: Text="9000"; # the port to bind too
}