@0xf0ef0a5c0aad9f4a; 


struct Schema {
  numhdd @0: UInt16; # expected number of hdds
  numssd @1: UInt16; # expected number of ssds
  ram @2: UInt64; # expected amount of ram (in mibi bytes - MiB)
  cpu @3: Text; # model name of expected cpu
  botid @4: Text; # id of the telegram bot
  chatid @5: Text; # id of the telegram groupchat
}
