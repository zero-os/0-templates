@0xd3397b8ab433d876;


struct Schema {
    status @0 :Status;
    hostname @1 :Text;
    nics @2 :List(Nic); # Configuration of the attached nics to the container
    portforwards @3 :List(PortForward);
    httpproxies @4 :List(HTTPProxy);
    domain @5: Text;
    advanced @6: Bool; # flag to check if http config has been set manually
    zerotiernodeid @7:Text;
    certificates @8 :List(Certificate);
    identity @9: Text;

    struct Nic {
        type @0: NicType;
        id @1: Text;
        config @2: NicConfig;
        name @3: Text;
        dhcpserver @4: DHCP;
        zerotierbridge @5: Bridge;
        token @6: Text;
    }

    struct Bridge {
        id @0: Text;
        token @1: Text;
    }
    struct CloudInit {
        userdata @0: Text;
        metadata @1: Text;
    }

    struct Host {
        macaddress @0: Text;
        hostname @1: Text;
        ipaddress @2: Text;
        ip6address @3: Text;
        cloudinit @4: CloudInit;
    }

    struct DHCP {
        nameservers @0: List(Text);
        hosts @1: List(Host);
    }

    struct NicConfig {
        cidr @0: Text;
        gateway @1: Text;
    }

    enum HTTPType {
        http @0;
        https @1;
    }

    struct HTTPProxy {
        host @0: Text;
        destinations @1: List(Text);
        types @2: List(HTTPType);
        name @3: Text;
    }

    enum Status{
        halted @0;
        running @1;
    }

    enum IPProtocol{
        tcp @0;
        udp @1;
    }

    struct PortForward{
        protocols @0: List(IPProtocol);
        srcport @1: Int32;
        srcip @2: Text;
        dstport @3: Int32;
        dstip @4: Text;
        name @5: Text;
    }
    enum NicType {
        default @0;
        zerotier @1;
        vlan @2;
        vxlan @3;
        bridge @4;
    }
    struct Certificate{
      path @0: Text;
      key @1: Text;
      metadata @2: Text;
      cert @3: Text;
    }
}
