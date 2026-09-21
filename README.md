Do not use UDP broadcast or multicast. Requires too much on the network config playing nice.
Instead just use a radio transmitter/receiver pair.
Hello

To do soon:
write a packet generator simulator script
broadcast these packets locally to simulate recieiving it (even though i will actually use a rf reciever)
upon receiving, store each section of the packet into a database corresponding to uuid

-> features:
    1. 3d attidude (pitch, yaw, roll)
    2. 2d map (lat/lon)
    3. velocity graphs (x,y,z)
