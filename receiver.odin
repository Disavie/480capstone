package receiver
import "core:net"
import "core:fmt"

import sqlite "./odin-sqlite3/"
import sa "./odin-sqlite3/addons/"


EXPECTED_GRP := "ABCD"

init_udp :: proc(_port : int = 5000,
            addr : net.IP4_Address = net.IP4_Address{127,0,0,1}
            ) -> net.UDP_Socket{
    endpt := net.Endpoint{
    address = addr,
    port = _port
  }

  any_sock, err := net.create_socket(
    net.Address_Family.IP4,
    net.Socket_Protocol.UDP,
    )
  if err != nil {panic("Error with socket creation")}
  sock := any_sock.(net.UDP_Socket)
  net.bind(sock,endpt)
  return sock
}

check_parity :: proc(buf: []byte, n : int) -> bool {
    count := 0

    for byte in buf {
        for i in 0..<8 {
            count += int((byte >> u8(i)) & 1)
        }
    }

    return count % 2 == 0
}

add_entry :: proc(db : ^sqlite.Connection, buf : []byte, field_width : int){
/*
  transmitter_name := buf[:4]
  q := sa.Query_Param{
    index = 0,
    value = Tx,
  }
  for i in 4..<len(buf){
   q := sa.Query_Param{
    index = i,
    value = buf[i:i+field_width]
   }
   sa.execute(db,i_instruc,q)
   i+=field_width 
  }
  */
}

main :: proc(){

  fmt.println("hello burger")
  // opening localhost udp channel, imitates receiving data from somewhere
  sock := init_udp()
  defer net.close(sock)

  //checking if database exists locally, if not create it
	db: ^sqlite.Connection

	if rc := sqlite.open("./data/db.sqlite", &db); rc != .Ok {
		fmt.panicf("failed to open database. result code {}", rc)
	}
	fmt.printfln("connected to database\n")
	defer {
		sqlite.close(db)
		fmt.printfln("\nconnection closed")
	}
  // Create transmitters table
  status := sa.execute(db, `
    CREATE TABLE IF NOT EXISTS transmitters(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
  ); 
  `)
  fmt.println(status, " ", sqlite.errmsg(db))
  if status != .Ok{
    sqlite.close(db)
    panic("not ok")
  }

  // Dummy entry
  if status := sa.execute(db,`
  INSERT INTO transmitters (id, name) VALUES (99,'BOB');
  `); status != .Ok{
    fmt.println(sqlite.errmsg(db))
    panic("fuhck")
  }


  /*
  '''
      'packet' format, add more info into this later
      everything from TIME..UZ will be a float
      PARITY can be a 1 bit even parity
      GROUP and UUID will be 8 bits each
      |GROUP|UUID|TIME|UX|UY|UZ|PARITY|
      GROUP, UUID -> 4 Bytes
      Data fields -> 4 Bytes (32 bits)
      Parity -> 1 bit + padding
  '''
  */
  buf: [25]byte
  field_width := 4
  for {
      n, remote, err := net.recv_udp(sock, buf[:])
      if err != nil {
          fmt.println("recv error:", err)
          continue
      }

      is_ok := check_parity(buf[:],n)
      if ! is_ok{
        panic("TRANSMISSION ERROR")
      }
      
    
      GRP := string(buf[:4]) // "Is this part of my transmitters group?"aaa
      Tx := buf[4:8]

      if GRP == EXPECTED_GRP{
        //add_entry(db, buf[4:], field_width)
        fmt.println("this is my dat'a")
        continue
      }


      fmt.printf(
          "received %d bytes from %s: %v\n",
          n,
          Tx,
          buf[:n],
      )
  }
}
