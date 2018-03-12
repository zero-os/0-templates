@0xa03ee920fb75e608;


struct Schema {
    zerotierClient @0: Text;
    # instance name of the zerotier client to use
    zerotierNetID @1: Text;
    # network ID of the zerotier network to use
    # for discover ZeroOs node

    wipeDisks @2 :Bool=false;
    # networks @2 :List(Text);
    # networks the new node needs to consume
    # Not implemented yet

    redisPassword @3 :Text;
    # jwt token used as password when
    # connecting to the node

}
