package receiver
import "core:net"
import "core:fmt"

main :: proc(){

  fmt.println("hello burger")

  UDP_PORT := 5000
//  UDP_IP = "127.0.0.1"

  endpt := net.Endpoint{
    address = net.IP4_Address{127,0,0,1},
    port = UDP_PORT
  }

  any_sock, err := net.create_socket(
    net.Address_Family.IP4,
    net.Socket_Protocol.UDP,
    )
  if err != nil{ panic("shit")}
  defer net.close(any_sock)
  sock := any_sock.(net.UDP_Socket)
  net.bind(sock,endpt)

  buf: [4096]byte
  for {
      n, remote, err := net.recv_udp(sock, buf[:])
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
