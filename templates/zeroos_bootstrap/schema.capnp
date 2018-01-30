@0xa9de4f7dcccf86af;

struct Schema {
    zerotierInstance @0: Text;
    # instance name of the zerotier client to use
    zerotierNetID @1: Text;
    # network ID of the zerotier network to use
    # for discover ZeroOs node

    wipedisks @2 :Bool=false;
    # networks @2 :List(Text);
    # networks the new node needs to consume
    # Not implemented yet


}
