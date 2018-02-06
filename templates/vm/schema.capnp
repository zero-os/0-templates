@0xb87ba7e9ff3d95db;



struct Schema {
    node @0: Text; # pointer to the parent service

    memory @1: UInt16 = 128; # Amount of memory in MiB
    cpu @2: UInt16 = 1; # Number of virtual CPUs
    nics @3: List(NicLink);
    vdisks @4: List(DiskLink);
    flist @5: Text; # if specified, the vm will boot from an flist and not a vdisk
    vnc @6: Int32 = -1; # the vnc port the machine is listening to


    struct NicLink {
      id @0: Text; # VxLan or VLan id
      type @1: NicType;
      macaddress @2: Text;
    }

    struct DiskLink {
      vdiskId @0: Text;
      maxIOps @1: UInt32;
    }

    enum NicType {
      default @0;
      vlan @1;
      vxlan @2;
      bridge @3;
    }
}