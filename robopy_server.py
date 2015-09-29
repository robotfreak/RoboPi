from __future__ import print_function
import asyncore
import socket
import select
import time
import sys
from pololu_drv8835_rpi import motors, MAX_SPEED 


class Client(asyncore.dispatcher_with_send):
    def __init__(self, socket=None, pollster=None):
        asyncore.dispatcher_with_send.__init__(self, socket)
        self.data = ''
        if pollster:
            self.pollster = pollster
            pollster.register(self, select.EPOLLIN)

    def handle_close(self):
        if self.pollster:
            self.pollster.unregister(self)

    def handle_read(self):
        receivedData = self.recv(8192)
        if not receivedData:
            self.close()
            return
        receivedData = self.data + receivedData
        while '\n' in receivedData:
            line, receivedData = receivedData.split('\n',1)
            self.handle_command(line)
        self.data = receivedData

    def handle_command(self, line):
#        cmd, line = line.split(' ', 2)
        if line == 'FW':
            self.send('OK\n')
            motor.setSpeed(MAX_SPEED, MAX_SPEED)
            print ('forward')
        elif line == 'BK':
            self.send('OK\n')
            motor.setSpeed(-MAX_SPEED, -MAX_SPEED)
            print ('backward')
        elif line == 'TL':
            self.send('OK\n')
            motor.setSpeed(-MAX_SPEED, MAX_SPEED)
            print ('turn left')
        elif line == 'TR':
            self.send('OK\n')
            motor.setSpeed(MAX_SPEED, -MAX_SPEED)
            print ('turn right')
        elif line == 'ST':
            self.send('OK\n')
            motor.setSpeed(0, 0)
            print ('stop')
        else:
            self.send('unknown command\n')
            print ('Unknown command:',line)
            motor.setSpeed(0, 0)



class Server(asyncore.dispatcher):
    def __init__(self, listen_to, pollster):
        asyncore.dispatcher.__init__(self)
        self.pollster = pollster
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(listen_to)
        self.listen(5)

    def handle_accept(self):
        newSocket, address = self.accept()
        print ("Connected from", address)
        Client(newSocket,self.pollster)

def readwrite(obj, flags):
    try:
        if flags & select.EPOLLIN:
            obj.handle_read_event()
        if flags & select.EPOLLOUT:
            obj.handle_write_event()
        if flags & select.EPOLLPRI:
            obj.handle_expt_event()
        if flags & (select.EPOLLHUP | select.EPOLLERR | select.POLLNVAL):
            obj.handle_close()
    except socket.error, e:
        if e.args[0] not in asyncore._DISCONNECTED:
            obj.handle_error()
        else:
            obj.handle_close()
    except asyncore._reraised_exceptions:
        raise
    except:
        obj.handle_error()


class EPoll(object):
    def __init__(self):
        self.epoll = select.epoll()
        self.fdmap = {}
    def register(self, obj, flags):
        fd = obj.fileno()
        self.epoll.register(fd, flags)
        self.fdmap[fd] = obj
    def unregister(self, obj):
        fd = obj.fileno()
        del self.fdmap[fd]
        self.epoll.unregister(fd)
    def poll(self):
        evt = self.epoll.poll()
        for fd, flags in evt:
            yield self.fdmap[fd], flags

class Motor(object):
    speedL = 0
    speedR = 0
    actSpeedL = 0
    actSpeedR = 0
    SPEED_STEP = 150

    def __init__(self):
      self.speedL = 0
      self.speedR = 0
      self.actSpeedL = 0
      self.actSpeedR = 0
 
    def setSpeed(self, sr, sl):
      self.speedL = sr
      self.speedR = sl
      print ("speed", self.speedR, self.speedL)

    def updateMotors(self):
      if self.speedL == 0:
        self.actSpeedL = 0
      elif self.actSpeedL < self.speedL:
        self.actSpeedL += self.SPEED_STEP
      elif self.actSpeedL > self.speedL:
        self.actSpeedL -= self.SPEED_STEP
      if self.speedR == 0:
        self.actSpeedR = 0
      elif self.actSpeedR < self.speedR:
        self.actSpeedR += self.SPEED_STEP
      elif self.actSpeedR > self.speedR:
        self.actSpeedR -= self.SPEED_STEP
      print ("motor lt, rt", self.actSpeedR, self.actSpeedL)
      motors.setSpeeds(self.actSpeedR, self.actSpeedL)
      time.sleep(0.100)

if __name__ == "__main__":
    print ('roboPi server started')
    motor = Motor()
    motors.setSpeeds(0, 0) 
    pollster = EPoll()
    pollster.register(Server(("",54321),pollster), select.EPOLLIN)
    while True:
        motor.updateMotors()
        evt = pollster.poll()
        for obj, flags in evt:
            readwrite(obj, flags)

