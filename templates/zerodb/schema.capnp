@0xbbc678cc7d18ad06;

struct Schema {
    listenAddr @0: Text="0.0.0.0";
    listenPort @1: UInt32=9900;
    dataDir @2: Text="/mnt/data";
    indexDir @3: Text="/mnt/index";
    mode @4: Mode;
    sync @5: Bool=false;
    container @6: Text;
    node @7: Text;
    diskMount @8: Text;
    admin @9: Text;

    enum Mode {
        user @0;
        seq @1;
        direct @2;
    }
}
