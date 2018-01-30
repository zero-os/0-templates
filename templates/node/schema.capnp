@0xc5ba0f64c9013a79;

struct Schema {
    id @0: Text; # mac address of the mngt network card
    hostname @1: Text;

    redisAddr @2 :Text; # redis addr for client
    redisPort @3 :UInt32 = 6379; # redis port for client
    redisPassword @4 :Text; # redis password for client
    version @5 :Text;
}
