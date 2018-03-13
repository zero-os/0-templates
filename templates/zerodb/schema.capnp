@0xbbc678cc7d18ad06;

struct Schema {
    listenPort @0: UInt32=9900; # zdb listen port
    dataDir @1: Text="/zerodb"; # data file directory (default /zerodb/)
    indexDir @2: Text="/zerodb"; # index file directory (default /zerodb/)
    mode @3: Mode; # a value from enum Mode representing the 0-db mode
    sync @4: Bool=false; # boolean indicating whether all write should be sync'd or not.
    container @5: Text; # reference to the container running the zerodb. This is set by the template.
    node @6: Text; # reference to the node running the zerdb container
    nodeMountPoint @7: Text; # the node mountpoint that will be mounted at containerMountPoint
    containerMountPoint @8: Text; # the container destination where hostMountPoint will be mounted
    admin @9: Text; # admin password

    enum Mode {
        user @0;
        seq @1;
        direct @2;
    }
}
