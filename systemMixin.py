import time
import os
import re
import subprocess


class PathNotExistsError(Exception):
    pass


class SystemMixin(object):
    """docstring for ClassName"""

    def set_path(self, force=True, **kwargs):
        if not hasattr(self, "context"):
            self.context = {}
        for attr, path in kwargs.items():
            if not os.path.exists(path):
                if force:
                    os.makedirs(path)
                else:
                    raise PathNotExistsError(
                        "Set path failed! Path of {} : {} does not exists.".format(attr, path))
            path = os.path.abspath(path)
            if os.path.isdir(path):
                path = path + '/'
            setattr(self, attr, path)
            self.context[attr] = path

    def set_attr(self, **kwargs):
        if not hasattr(self, "context"):
            self.context = {}
        for attr, val in kwargs.items():
            if not attr == "self":
                setattr(self, attr, val)
                print("The {} is {}".format(" ".join(attr.split("_")), str(val)))
                self.context[attr] = val

    def get_attrs(self, obj):
        return {attr: val for attr, val in obj.__dict__.items() if not attr.startswith('__')}

    def system(self, cmd, escape_sge=False, **kwargs):
        if not hasattr(self, "context"):
            self.context = {}
        context = self.context.copy()
        context.update(kwargs)
        cmd = cmd.format(**context)
        cmd = cmd.strip()
        if escape_sge:
            cmd = re.sub('\|[^\|]+$', '', cmd)
            cmd = re.sub('^echo', '', cmd)
            cmd = cmd.strip(" |'")
        cmd_name = cmd.split()[0]
        t1 = time.time()
        print("\033[0;32;40m############Running command: {}\n{}\n\033[0m".format(
            cmd_name, cmd))
        # os.system(cmd)
        subprocess.call(["bash", "-c", cmd])
        time_took = (time.time() - t1) / 60
        print("\033[0;32;40m############{} done, time took: {} minutes\033[0m".format(
            cmd_name, time_took))
