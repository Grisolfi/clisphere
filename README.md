# CLISphere

A shell utility to navigate through esxi/vcenter hosts using vsphere-api

## Usage

Is strongly recommended that you create a virtualenv, so you should follow the steps below:

1. `virtualenv -p python3 env`
1. `source env/bin/activate`
1. `pip3 install requirements.txt`
1. `python3 prompt.py -s HOST -u USER [-p PASSWORD] [-o PORT]`

## References

* https://github.com/vmware/pyvmomi-community-samples/issues/464
* http://vijava.sourceforge.net/vSphereAPIDoc/ver5/ReferenceGuide/index-mo_types.html
* http://vijava.sourceforge.net/vSphereAPIDoc/ver5/ReferenceGuide/vim.VirtualMachine.html
* https://github.com/vmware/pyvmomi-community-samples
* https://stackoverflow.com/questions/5458048/how-to-make-a-python-script-standalone-executable-to-run-without-any-dependency
* https://github.com/vmware/pyvmomi
* https://github.com/vmware/vsphere-guest-run
