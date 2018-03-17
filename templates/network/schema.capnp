@0xeee35f60471101a3;

struct Schema {
    vlanTag @0 :UInt16;
    cidr @1 :Text; # of the storage network
    bonded @2 :Bool=false;
    driver @3 :Text;
    # specify this in case the driver requires reloading
}