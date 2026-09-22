package receiver
import "core:net"
import "core:fmt"
import "core:os"

import sqlite "./odin-sqlite3/"
import sa "./odin-sqlite3/addons/"


EXPECTED_GRP := "ABCD"
Transmitter_Row :: struct {
    id: i64 `sqlite:"id"`,
}

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
add_entry :: proc(db: ^sqlite.Connection, transmitter_id: i64, data: []byte, field_width: int) {
    timestamp := (^f32)(&data[0])^
    ux := (^f32)(&data[4])^
    uy := (^f32)(&data[8])^
    uz := (^f32)(&data[12])^

    if status := sa.execute(db, `
        INSERT INTO entries (transmitter_id, timestamp, ux, uy, uz)
        VALUES (?, ?, ?, ?, ?);
    `, []sa.Query_Param{
        {index = 1, value = transmitter_id},
        {index = 2, value = f64(timestamp)},
        {index = 3, value = f64(ux)},
        {index = 4, value = f64(uy)},
        {index = 5, value = f64(uz)},
    }); status != .Ok {
        fmt.println("insert entry failed:", sqlite.errmsg(db))
    }
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
  if status := sa.execute(db, "PRAGMA foreign_keys = On"); status != .Ok{
    sqlite.close(db)
    panic("Keys not happy")
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
    name TEXT NOT NULL UNIQUE
  ); 
  `)
  fmt.println(status, " ", sqlite.errmsg(db))
  if status != .Ok{
    sqlite.close(db)
    panic("Error with table creation")
  }

  // Dummy entry
  if status := sa.execute(db,`
  INSERT INTO transmitters (id,name) VALUES (99, "TEST0");
  `); status != .Ok{
    fmt.println(sqlite.errmsg(db))
    panic("Error with dummy insert")
  }


  if status := sa.execute(db, `
      CREATE TABLE IF NOT EXISTS entries(
      id INTEGER PRIMARY KEY,
      transmitter_id INTEGER NOT NULL,
      timestamp INTEGER NOT NULL,
      ux REAL,
      uy REAL,
      uz REAL,
      FOREIGN KEY (transmitter_id) REFERENCES transmitters(id)
      );
  `); status != .Ok {
      fmt.println("create entries failed:", sqlite.errmsg(db))
      sqlite.close(db)
      os.exit(1)
  }

  // Create index on entries(transmitter_id, timestamp)
  if status := sa.execute(db, `
      CREATE INDEX IF NOT EXISTS idx_entries_transmitter_time
      ON entries(transmitter_id, timestamp);
  `); status != .Ok {
      fmt.println("create index failed:", sqlite.errmsg(db))
      sqlite.close(db)
      os.exit(1)
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
      tx_uuid := string(buf[4:8])

      if GRP == EXPECTED_GRP{
          if status := sa.execute(db, `
              INSERT OR IGNORE INTO transmitters (name) VALUES (?);
          `, []sa.Query_Param{
              {index = 1, value = tx_uuid},
          }); status != .Ok {
              fmt.println("insert transmitter failed:", sqlite.errmsg(db))
          }

          rows: [dynamic]Transmitter_Row
          defer delete(rows)

          if status := sa.query(db, &rows, `
              SELECT id FROM transmitters WHERE name = ?;
          `, []sa.Query_Param{
              {index = 1, value = tx_uuid},
          }); status != .Ok {
              fmt.println("lookup transmitter id failed:", sqlite.errmsg(db))
              continue
          }

          if len(rows) == 0 {
              fmt.println("no transmitter found for uuid:", tx_uuid)
              continue
          }

          transmitter_id := rows[0].id
          add_entry(db, transmitter_id, buf[8:], field_width)
      }
      
      fmt.printf(
          "received %d bytes from %s: %v\n",
          n,
          tx_uuid,
          buf[:n],
      )
  }
}
