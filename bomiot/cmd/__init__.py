import os

if "RUN_LAN" not in os.environ:
    from bomiot.cmd.cmd import cmd