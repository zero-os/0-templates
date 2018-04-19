@0xbbc678cc7d18ad06;

struct Schema {
    mode @0: Mode=direct; # a value from enum Mode representing the 0-db mode
    sync @1: Bool=false; # boolean indicating whether all write should be sync'd or not.
    disk @2: Text; # path of the disk to use
    nodePort @3: Int32; # the node port used in the portfowarding

    enum Mode {
        user @0;
        seq @1;
        direct @2;
    }
}
