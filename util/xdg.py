import configparser
import os

def initXDG(program_name):
    # per the XDG basedir-spec we adhere to $XDG_CONFIG_HOME if it's set, otherwise assume $HOME/.config
    xdg_config_home = ''
    if 'XDG_CONFIG_HOME' in os.environ:
        xdg_config_home = os.environ['XDG_CONFIG_HOME']
    else:
        xdg_config_home = "%s/.config" % os.path.expanduser('~')

    # XDG base-dir: "If, when attempting to write a file, the destination directory is non-existant an attempt should be made to create it with permission 0700. If the destination directory exists already the permissions should not be changed."
    if not os.path.isdir(xdg_config_home):
        os.mkdir(xdg_config_home, 0o0700)

    # finally create our own config dir
    config_dir = "%s/%s" % (xdg_config_home, program_name)
    if not os.path.isdir(config_dir):
        os.mkdir(config_dir, 0o0700)

    return config_dir + '/'
