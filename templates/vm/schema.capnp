@0xb87ba7e9ff3d95db;



struct Schema {
    memory @0: UInt16 = 128; # Amount of memory in MiB
    cpu @1: UInt16 = 1; # Number of virtual CPUs
    nics @2: List(NicLink);
    flist @3: Text; # if specified, the vm will boot from an flist and not a vdisk
    vnc @4: Int32 = -1; # the vnc port the machine is listening to
    ports @5:List(Text); # List of node to vm port mappings. e.g: 8080:80
    media @6: List(Media); # list of media to attach to the vm
    tags @7: List(Text); # list of tags
    configs @8: List(Config); # list of config

    struct Config {
        path @0: Text;
        content @1: Text;
    }
    struct Media {
      type @0: MediaType;
      url @1: Text;
    }

    enum MediaType {
      disk @0;
      cdrom @1;
    }

    struct NicLink {
      id @0: Text; # VxLan or VLan id
      type @1: NicType;
      macaddress @2: Text;
    }

    enum NicType {
      default @0;
      vlan @1;
      vxlan @2;
      bridge @3;
    }
}
