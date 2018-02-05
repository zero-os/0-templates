@0xb87ba7e9ff3d95db;



struct Schema {
    node @0: Text; # pointer to the parent service
    id @1: Text;

    memory @2: UInt16 = 128; # Amount of memory in MiB
    cpu @3: UInt16 = 1; # Number of virtual CPUs
    nics @4: List(NicLink);
    vdisks @5: List(DiskLink);
    flist @6: Text; # if specified, the vm will boot from an flist and not a vdisk
    vnc @7: Int32 = -1; # the vnc port the machine is listening to


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