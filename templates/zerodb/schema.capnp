@0xbbc678cc7d18ad06;

struct Schema {
    listenAddr @0: Text="0.0.0.0"; # zdb listen address
    listenPort @1: UInt32=9900; # zdb listen port
    dataDir @2: Text="/zerodb"; # data file directory (default /zerodb/)
    indexDir @3: Text="/zerodb"; # index file directory (default /zerodb/)
    mode @4: Mode; # a value from enum Mode representing the 0-db mode
    sync @5: Bool=false; # boolean indicating whether all write should be sync'd or not.
    container @6: Text; # reference to the container running the zerodb. This is set by the template.
    node @7: Text; # reference to the node running the zerdb container
    nodeMountPoint @8: Text; # the node mountpoint that will be mounted at containerMountPoint
    containerMountPoint @9: Text; # the container destination where hostMountPoint will be mounted
    admin @10: Text; # admin password

    enum Mode {
        user @0;
        seq @1;
        direct @2;
    }
}
