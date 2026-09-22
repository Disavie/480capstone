package receiver
import "core:net"
import "core:fmt"

main :: proc(){

  fmt.println("hello burger")

  UDP_PORT := 5000

  endpt := net.Endpoint{
    address = net.IP4_Address{0,0,0,0},
    port = UDP_PORT
  }

  sock, err := net.create_socket(
    net.Address_Family.IP4,
    net.Socket_Protocol.UDP,
    )
  if err == nil{ panic("shit")}
  defer net.close(sock)

  net.bind(sock,endpt)
  for {
      n, remote, err := net.recv_from(socket, buf[:])
      if err != nil {
          fmt.println("recv error:", err)
          continue
      }

      fmt.printf(
          "received %d bytes from %v: %v\n",
          n,
          remote,
          buf[:n],
      )
  }
}
