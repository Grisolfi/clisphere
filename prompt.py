from cmd import Cmd
from pyVim.connect import SmartConnectNoSSL
from pyVim.connect import Disconnect
from pyVmomi import vim
from pyVmomi.VmomiSupport import ManagedObject
from subprocess import call

import sys, tempfile, os
import argparse
import getpass
import atexit
import os
import copy
            
class Decoration:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   WHITE = '\u001b[37m'
   END = '\033[0m'

class Prompt(Cmd):

    path = ''

    def __init__(self, obj, name):
        super(Prompt, self).__init__()
        self.obj = obj
        self.context = name
        if isinstance(obj, list):
            self.children = {children.name:children for children in obj}
        elif not isinstance(obj, bool):
            self.children = {children.name:getattr(self.obj, children.name) for children in self.obj._GetPropertyList()}
        else:
            self.children = None

    def _gen_prompt(self, context):
        return '{0}@{1}:({2})> '.format(params.get('user'), params.get('host'), context)

    def emptyline(self):
        pass
    
    def default(self, s):
        print('CLISphere: {0}: command not found'.format(s))

    def preloop(self):
        self.ruler = '-'
        self.prompt = self._gen_prompt(self.context)

    def do_ls(self, s):
        prompt = self
        if s in self.children:
            prompt = Prompt(self.children.get(s), s)
        ordered = list(prompt.children.keys())
        ordered.sort()
        for child_name in ordered:
            key = child_name
            
            if not prompt.children.get(key):
                child_name = Decoration.BOLD + Decoration.RED + key + Decoration.END
            elif '_GetPropertyList' in dir(prompt.children.get(key)) or isinstance(prompt.children.get(key), list) and prompt.children.get(key).__class__.Item is ManagedObject:
                child_name = Decoration.BOLD + Decoration.BLUE + key + Decoration.END
            else:
                child_name = Decoration.BOLD + Decoration.WHITE + key + Decoration.END
            print('{:<82s} {:<50}'.format(child_name, type(prompt.children.get(key)).__name__))

    def do_cd(self, s):
        if s == '..' and not self.context == 'HostSystem':
            return True
        if self.children.get(s) and s in self.children and '_GetPropertyList' in dir(self.children.get(s)) or self.children.get(s) and self.children.get(s).__class__.Item is ManagedObject:
            children = Prompt(self.children.get(s), s)
            children.cmdloop()

    def do_cat(self, s):
        if s in self.children.keys():
            print(self.children.get(s))

    def do_less(self, s):
        if self.children.get(s) and s in self.children.keys():
            initial_message = str(self.children.get(s))
            with tempfile.NamedTemporaryFile(suffix=".tmp", mode='w+') as tf:
                tf.write(initial_message)
                tf.flush()
                call(['less', tf.name])

    def do_summary(self, s):
        print('children is root?', self.root.keys() == self.children.keys())
        print('root', self.root.keys())
        print('children', self.children.keys())
        # summary = Summary(self.root)
        # print(summary.get_power_policy())

    def complete_cd(self, text, line, begidx, endidx):
         return [i for i in self.children if i.startswith(text)]

    complete_cat = complete_cd
    complete_less = complete_cd
    complete_ls = complete_cd

    def __str__(self):
        return self.name

    def do_exit(self, s):
        if self.context == 'HostSystem':
            choice = input('\nexit anyway ? (yes/no): ') 
            if choice == 'yes' or choice == 'y':
                return True
            else:
                return False
        print('\n')
        return True

    do_EOF = do_exit

    def do_shell(self, s):
        os.system(s)
    
    def help_shell(self):
        print ("execute shell commands")


def main():
    service_instance = SmartConnectNoSSL(**params)
    content = service_instance.RetrieveContent()
    atexit.register(Disconnect, service_instance)
    objview = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    esxi_hosts = objview.view
    objview.Destroy()
    prompt = Prompt(esxi_hosts, 'HostSystem')
    prompt.cmdloop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Process args for retrieving all the Virtual Machines')

    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='Remote host to connect to')
    
    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host')

    parser.add_argument('-o', '--port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on')

    args = parser.parse_args()
    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password for host {0} and user {1}: '.format(args.host, args.user))
    params = {
        'host': args.host,
        'user': args.user,
        'pwd': args.password,
        'port': args.port
    }
    try:
        main()
    except KeyboardInterrupt:
        pass 
    except vim.fault.InvalidLogin:
        print('\nInvalid credentials, try again')
    except vim.NotAuthenticated:
        print('\nSession expired.')
