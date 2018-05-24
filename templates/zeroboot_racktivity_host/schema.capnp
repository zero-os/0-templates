@0xfefdee2e4b947c50;

struct Schema {
    zerobootClient @0: Text; # Zeroboot client instance name
    racktivityClient @1: Text; # Racktivity client instance name
    network @2: Text; # Zeroboot network that contains the host
    mac @3: Text; # Target mac address
    ip @4: Text; # Target IP address
    hostname @5: Text; # Hostname of target
    ipxeUrl @6: Text; # URL to ipxe script
    racktivityPort @7: Int32; # Target's port on the Racktivity device
    racktivityPowerModule @8: Text; # Racktivity module ID (only Racktivity for SE models)
    powerState @9: Bool; # Internally saved powerstate
}
