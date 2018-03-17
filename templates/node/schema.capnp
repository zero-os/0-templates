@0xc5ba0f64c9013a79;

struct Schema {
    hostname @0: Text;
    redisAddr @1 :Text; # redis addr for client
    redisPort @2 :UInt32 = 6379; # redis port for client
    redisPassword @3 :Text; # redis password for client
    version @4 :Text;
    networks @5 :List(Text); # network configuration
}
