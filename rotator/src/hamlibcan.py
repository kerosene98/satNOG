import socketserver

def read_sensors():
    return '33.000000\n33.000000\n'.encode('ascii')

def set_position(az, el):
    pass

class MyTCPHandler(socketserver.StreamRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):

        # self.request is the TCP socket connected to the client
        while(1):
            try:
                print('LOOP')
                self.data = self.rfile.readline().strip()
                print(repr(self.data))
                command = self.data.decode('utf-8')
                if command == '\dump_state':
                    rig_capps = [
                        # rigctl protocol version 
                        "0\n",
                        # rigctl model 
                        "2\n",
                        # ITU region 
                        "1\n",
                        # RX/TX frequency ranges
                        #  * start, end, modes, low_power, high_power, vfo, ant
                        #  *  start/end - Start/End frequency [Hz]
                        #  *  modes - Bit field of RIG_MODE's (AM|CW|CWR|USB|LSB|FM|WFM)
                        #  *  low_power/high_power - Lower/Higher RF power in mW,
                        #  *                         -1 for no power (ie. rx list)
                        #  *  vfo - VFO list equipped with this range (RIG_VFO_A)
                        #  *  ant - Antenna list equipped with this range, 0 means all
                        #  *  FIXME: limits can be gets from receiver::get_rf_range()
                        
                        "0.000000 10000000000.000000 0xef -1 -1 0x1 0x0\n",
                        # End of RX frequency ranges. 
                        "0 0 0 0 0 0 0\n",
                        # End of TX frequency ranges. The Gqrx is reciver only. 
                        "0 0 0 0 0 0 0\n"
                    ]
                    self.request.sendall(''.join(rig_capps).encode('ascii'))
                    print('sent response: Magic numbers :/')
                elif command == 'p':
                    print('received command: ' + command)
                    data = read_sensors()
                    self.request.sendall(data)
                    print('sent response: ' + repr(data))
                elif command[0] == 'P':
                    _, az, el = command.split(' ')
                    set_position(az, el)
                    self.request.sendall('RPRT 0\n'.encode('ascii'))
                    print('sent response: RPRT 0\n' )
                else:
                    self.request.sendall('RPRT -4\n'.encode('ascii'))
                    print('unknown command: ' + str(self.data))
                    print('sent response: RPRT -4\n')
            except:
                break
if __name__ == "__main__":
    HOST, PORT = "localhost", 4333
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler, bind_and_activate=False)
    server.allow_reuse_address=True
    server.server_bind()
    server.server_activate()
    server.serve_forever()