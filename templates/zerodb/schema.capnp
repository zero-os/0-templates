@0xbbc678cc7d18ad06;

struct Schema {
    mode @0: Mode=direct; # a value from enum Mode representing the 0-db mode
    sync @1: Bool=false; # boolean indicating whether all write should be sync'd or not.
    disk @2: Text; # path of the disk to use
    nodePort @3: Int32; # the node port used in the portforwarding
    admin @4: Text; # admin password
    namespaces @5: List(Namespace); # a list of namespaces deployed on this zerodb

    enum Mode {
        user @0;
        seq @1;
        direct @2;
    }

    struct Namespace {
        name @0: Text; # name of the namespace
        size @1: Int32; # the maximum size in GB for the namespace
        password @2: Text; # password for the namespace
        public @3: Bool=true; # boolean indicating if it is public or not
    }
}
