@0xbec2e1d1f82225f1;


struct Schema {
    size @0: Int32; # size of the namespace
    disktype @1 :DiskType; # type of disk to use for this namespace
    mountpoint @2 :Text;
    filesystem @3 :Text;
    zerodb @4 :Text; # instance name of the zerodb where the namespace is deployed. User don't have to fill this attribute

    enum DiskType{
        hdd @0;
        ssd @1;
    }
}
