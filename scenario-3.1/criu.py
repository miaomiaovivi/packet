import os


class CRIU(object):
    """
    A CRIU object that will run appropriate command for taking a snapshot of
    the process you are interested in. You should be preparing the appropriate
    criu command to execute, just that, the same command is executed via python
    instead of being executed via shell.
    """

    def __init__(self, image_dir, prev_image_dir):
        """
        set an image_dir where the snapshot of the directory will be stored.
        for incremental dumps, you will also need to setup a prev_image_dir.
        """
        self._image_dir = image_dir
        self._prev_image_dir = prev_image_dir

    def _execute(self, cmd):
        """
        just pass the command as cmd exactly the way you would write this
        command in shell. Eg: If in shell you write 'echo "Hello, world"' to
        print Hello, world. For doing the same you should pass
        'echo "Hello, world"' in cmd.
        """
        print "Executing: %s" % cmd
        os.system(cmd)

    def pre_dump(self, pid):
        """
        useful for iterative dump, the CRIU allow the users to take a dump
        into a particular directory. All future dump instructions will have a
        differential content from its previous dump instruction.
        """
        print "pre dump"
        #TODO - COMPLETE ME

    def dump(self, pid):
        """
        dump the current process into the images dir. Please set the
        appropriate options for the criu dump command that you will be using
        here
        """
        print "dump"
        #TODO - COMPLETE ME

    def restore(self):
        """
        restore the process based on the dump content saved in images dir.
        Please set the appropriate options for the criu restore command that
        you will be using here
        """
        print "restore"
        #TODO - COMPLETE ME
