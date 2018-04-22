@0xc5ba0f64c9013a79;

struct Schema {
    hostname @0: Text;
    version @1 :Text;
    uptime @2: Float64; # node up time in seconds
    deployZdb @3: Bool; # if true deploy 0-db on each disk
}
