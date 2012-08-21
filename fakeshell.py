#!/usr/bin/python2
#
#   BOFH Login Script
#
#   Based on the login script from BOFH #13 by Simon Travaglia
import getpass
import os
import platform
import socket
import sys


sudomsg = '''usage: sudo [-D level] -h | -K | -k | -V
usage: sudo -v [-AknS] [-D level] [-g groupname|#gid] [-p prompt] [-u user
            name|#uid]
usage: sudo -l[l] [-AknS] [-D level] [-g groupname|#gid] [-p prompt] [-U user
            name] [-u user name|#uid] [-g groupname|#gid] [command]
usage: sudo [-AbEHknPS] [-C fd] [-D level] [-g groupname|#gid] [-p prompt] [-u
            user name|#uid] [-g groupname|#gid] [VAR=value] [-i|-s] [<command>]
usage: sudo -e [-AknS] [-C fd] [-D level] [-g groupname|#gid] [-p prompt] [-u
            user name|#uid] file ...'''


class FakeShell(object):
    def __init__(self):
        """Get user info."""
        self.uname = getpass.getuser()
        self.home = os.environ['HOME']
        self.hostname = socket.gethostname()
        self.files = os.listdir(self.home)
        self.distro = platform.dist()
        if self.distro[0] == 'gentoo':
            self.prompt = '%(uname)s@$(hostname)s %(pwd)s $ '
        else:
            # Default to Ubuntu/Debian prompt.
            self.prompt = '%(uname)s@%(hostname)s:%(pwd)s$ '

    def showPrompt(self):
        """Show the main login prompt."""
        sys.stdout.write('Yes means No and No Means Yes. Delete all files? '
            '[Y] ')
        rv = raw_input()
        if rv.lower() not in ('y', 'yes', 'no', 'n'):
            print('Unrecognized option. Assuming Y.')
        return True

    def fakeRm(self):
        """Simulate rm -rfv ~"""
        os.chdir(self.home)
        files = list(self.files)
        length = len(self.files)
        try:
            for i in xrange(length):
                if os.path.isdir(os.path.join(self.home, self.files[i])):
                    print('removed directory `%(dir)s\''
                        % {'dir': self.files[i]})
                else:
                    print('removed `%(dir)s\'' % {'dir': self.files[i]})
                files.remove(self.files[i])
        except:
            pass
        self.files = files
        if self.files == []:
            return True

    def fakeSh(self):
        """Create a fake sh environment."""
        loop = True
        pwd = '~'
        while loop:
            cmd = raw_input(self.prompt
                % {'uname': self.uname,
                   'hostname': self.hostname,
                   'pwd': pwd})
            for l in ('A', 'B', 'C', 'D'):
                cmd = cmd.replace('\x1b[%s' % l, '')
            cmds = cmd.split(' ')
            if cmds == ['exit']:
                loop = False
                return True
            elif cmd == 'echo $PATH':
                pass
            elif cmds == ['']:
                pass
            elif cmds[0] == 'sudo':
                if len(cmds) == 1:
                    print(sudomsg)
                else:
                    print('%(uname)s is not in the sudoers file.'
                          ' This incident will be reported.'
                        % {'uname': self.uname})
            elif 'ls' in cmds and pwd == '~':
                pass
            else:
                print('%(cmd)s: command not found' % {'cmd': cmd})

    def mainLoop(self):
        """Loop while the (l)user hasn't figure out how to exit."""
        run = True
        rv = None
        deleted = None
        while run:
            try:
                if rv is None:
                    rv = self.showPrompt()
                if deleted is None:
                    deleted = self.fakeRm()
                run = self.fakeSh()
            except KeyboardInterrupt:
                sys.stdout.write('\n')
                pass
            except EOFError:
                sys.stdout.write('\n')
                pass
            except:
                pass


if __name__ == '__main__':
    sh = FakeShell()
    sh.mainLoop()
