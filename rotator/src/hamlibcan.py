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
                self.data = self.rfile.readline().strip()

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
                        "0 0 0 0 0 0 0\n",
                        # Tuning steps: modes, tuning_step 
                        "0xef 1\n",
                        "0xef 0\n",
                        # End of tuning steps 
                        "0 0\n",
                        # Filter sizes: modes, width 
                        "0x82 500\n",    # CW | CWR normal 
                        "0x82 200\n",    # CW | CWR narrow 
                        "0x82 2000\n",   # CW | CWR wide 
                        "0x21 10000\n",  # AM | FM normal 
                        "0x21 5000\n",   # AM | FM narrow 
                        "0x21 20000\n",  # AM | FM wide 
                        "0x0c 2700\n",   # SSB normal 
                        "0x0c 1400\n",   # SSB narrow 
                        "0x0c 3900\n",   # SSB wide 
                        "0x40 160000\n", # WFM normal 
                        "0x40 120000\n", # WFM narrow 
                        "0x40 200000\n", # WFM wide 
                        # End of filter sizes  
                        "0 0\n",
                        # max_rit  
                        "0\n",
                        # max_xit 
                        "0\n",
                        # max_ifshift 
                        "0\n",
                        # Announces (bit field list) 
                        "0\n", # RIG_ANN_NONE 
                        # Preamp list in dB, 0 terminated 
                        "0\n",
                        # Attenuator list in dB, 0 terminated 
                        "0\n",
                        # Bit field list of get functions 
                        "0\n", # RIG_FUNC_NONE 
                        # Bit field list of set functions 
                        "0\n", # RIG_FUNC_NONE 
                        # Bit field list of get level 
                        "0x40000020\n", # RIG_LEVEL_SQL | RIG_LEVEL_STRENGTH 
                        # Bit field list of set level 
                        "0x20\n",       # RIG_LEVEL_SQL 
                        # Bit field list of get parm 
                        "0\n", # RIG_PARM_NONE 
                        # Bit field list of set parm 
                        "0\n", # RIG_PARM_NONE )
                    ]
                    
                    self.request.sendall(''.join(rig_capps).encode('ascii'))
                elif command == 'p':
                    data = read_sensors()
                    self.request.sendall(data)
                elif command[0] == 'P':
                    _, az, el = command.split(' ')
                    set_position(az, el)
                    self.request.sendall('RPRT 0\n'.encode('ascii'))
                else:
                    print('unknown request: ' + self.data)
                    self.request.sendall('RPRT -4\n'.encode('ascii'))
            except:
                break
if __name__ == "__main__":
    HOST, PORT = "localhost", 4533
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler, bind_and_activate=False)
    server.allow_reuse_address=True
    server.server_bind()
    server.server_activate()
    server.serve_forever()