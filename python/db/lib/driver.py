#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 13 Aug 2012 16:19:18 CEST 

"""An abstract class that defines the required behavior of implemented
databases.
"""

import os
import abc
from .utils import makedirs_safe

def dbshell(arguments):
  """Drops you into a database shell"""

  import subprocess

  dbfile = os.path.join(arguments.location, arguments.files[0])

  if arguments.type == 'sqlite': 
    prog = 'sqlite3'
  else: 
    raise RuntimeError, "Error auxiliary database file '%s' cannot be used to initiate a database shell connection (type='%s')" % (dbfile, arguments.type)

  arguments = [prog, dbfile]

  try:
    if arguments.dryrun:
      print "[dry-run] exec '%s'" % ' '.join(arguments)
      return 0
    else:
      p = subprocess.Popen(arguments)
  except OSError as e:
    # occurs when the file is not executable or not found
    print("Error executing '%s': %s (%d)" % (' '.join(arguments), e.strerror,
        e.errno))
    sys.exit(e.errno)
  
  try:
    p.communicate()
  except KeyboardInterrupt: # the user CTRL-C'ed
    import signal
    os.kill(p.pid, signal.SIGTERM)
    return signal.SIGTERM

  return p.returncode

def dbshell_command(subparsers):
  """Adds a new dbshell subcommand to your subparser"""

  parser = subparsers.add_parser('dbshell', help=dbshell.__doc__)
  parser.add_argument("-n", "--dry-run", dest="dryrun", default=False,
      action='store_true',
      help="does not actually run, just prints what would do instead")
  parser.set_defaults(func=dbshell)

def print_location(arguments):
  """Prints the current location of the database SQL file."""
  
  for k in arguments.files: print(os.path.join(arguments.location, k))

  return 0

def location_command(subparsers):
  """Adds a new location subcommand to your parser"""

  parser = subparsers.add_parser('location', help=print_location.__doc__)
  parser.set_defaults(func=print_location)

  return parser

def get(arguments):
  """Copies the database auxiliary files from a given directory to their installed working location."""

  from .download import download
  import shutil

  for f in arguments.files:
    src = '/'.join((arguments.url, arguments.name, arguments.version, f))
    dest = os.path.join(arguments.location, f)

    if not os.path.exists(arguments.location):
      if arguments.verbose: 
        print "Creating directory '%s'..." % arguments.location

      makedirs_safe(os.path.dirname(dest), arguments.dryrun)

    if os.path.exists(dest):
      if arguments.verbose: print "Removing existing copy '%s'..." % dest

      if arguments.dryrun:
        print "[dry-run] rm -f '%s'" % dest
      else:
        os.unlink(dest)

    if arguments.verbose: print "Getting %s -> %s" % (src, dest)

    if src.find('http') == 0: #must download
      if arguments.dryrun: 
        print "[dry-run] wget --output-document=%s %s" % (dest, src)
      else: 
        download(src, dest, arguments.verbose)
    else:
      if arguments.dryrun: 
        print "[dry-run] cp %s %s" % (src, dest)
      else: 
        shutil.copy2(src, dest)

  return 0

def get_command(subparsers):
  
  parser = subparsers.add_parser('get', help=get.__doc__)
  parser.add_argument("-n", "--dry-run", dest="dryrun", default=False,
      action='store_true',
      help="does not actually run, just prints what would do instead")
  parser.add_argument('-v', '--verbose', dest="verbose", default=False,
      action='store_true', help="produces more output while copying")
  parser.add_argument('-V', '--version', dest="version",
      help="if set, overrides the default version set for this package when putting the database files on the given directory")
  parser.add_argument('url', default="http://www.idiap.ch/software/bob/databases", 
      help="sets the URL to which the database will be downloaded from (defaults to '%(default)s')",
      nargs="?")
  parser.set_defaults(func=get)

  return parser

def put(arguments):
  """Copies database auxiliary files from their official work location to a
  given directory."""

  import shutil

  d = os.path.join(arguments.directory, arguments.name, arguments.version)
  for f in arguments.files:
    dest = os.path.join(d, f)
  
    makedirs_safe(os.path.dirname(dest), arguments.dryrun)

    if os.path.exists(dest):
      if arguments.verbose: print "Removing existing file '%s'..." % dest
      
      if arguments.dryrun:
        print "[dry-run] rm -f '%s'" % dest
      else:
        os.unlink(dest)

    src = os.path.join(arguments.location, f)
    
    if arguments.verbose: print "Putting %s -> %s..." % (src, dest)

    if arguments.dryrun: print "[dry-run] cp %s -> %s" % (src, dest)
    else: shutil.copy2(src, dest)

  return 0

def put_command(subparsers):
  
  parser = subparsers.add_parser('put', help=put.__doc__)
  parser.add_argument("-n", "--dry-run", dest="dryrun", default=False,
      action='store_true',
      help="does not actually run, just prints what would do instead")
  parser.add_argument('-v', '--verbose', dest="verbose", default=False,
      action='store_true', help="produces more output while copying")
  parser.add_argument('-V', '--version', dest="version",
      help="if set, overrides the default version set for this package when putting the database files on the given directory")
  parser.add_argument('directory', help="sets the directory to which the database will be copied to")
  parser.set_defaults(func=put)

  return parser

def version(arguments):
  """Outputs the database version"""

  print '%s == %s' % (arguments.name, arguments.version)

  return 0

def version_command(subparsers):

  parser = subparsers.add_parser('version', help=put.__doc__)
  parser.set_defaults(func=version)

  return parser

class Interface(object):
  """Base manager for Bob databases"""

  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def name(self):
    '''Returns a simple name for this database, w/o funny characters, spaces'''
    return

  @abc.abstractmethod
  def location(self):
    '''Returns the directory that contains the data'''
    return

  @abc.abstractmethod
  def files(self):
    '''Returns a python iterable with all auxiliary files needed.
    
    The values should be take w.r.t. where the python file that declares the
    database is sitting at.
    '''
    return

  @abc.abstractmethod
  def version(self):
    '''Returns the current version number defined in setup.py'''
    return

  @abc.abstractmethod
  def type(self):
    '''Returns the type of auxiliary files you have for this database
    
    If you return 'sqlite', then we append special actions such as 'dbshell'
    on 'bob_dbmanage.py' automatically for you. Otherwise, we don't.

    If you use auxiliary text files, just return 'text'. We may provide
    special services for those types in the future.

    Use the special name 'builtin' if this database is an integral part of Bob.
    '''
    return

  def setup_parser(self, parser, short_description, long_description):
    '''Sets up the base parser for this database.
    
    Keyword arguments:

    short_description
      A short description (one-liner) for this database

    long_description
      A more involved explanation of this database

    Returns a subparser, ready to be added commands on
    '''

    from argparse import RawDescriptionHelpFormatter

    # creates a top-level parser for this database
    top_level = parser.add_parser(self.name(),
        formatter_class=RawDescriptionHelpFormatter,
        help=short_description, description=long_description)

    type = self.type()
    files = self.files()

    top_level.set_defaults(name=self.name())
    top_level.set_defaults(location=self.location())
    top_level.set_defaults(version=self.version())
    top_level.set_defaults(type=type)
    top_level.set_defaults(files=files)
    
    subparsers = top_level.add_subparsers(title="subcommands")

    # adds some stock commands
    version_command(subparsers)

    if type in ('sqlite',):
      dbshell_command(subparsers)

    if files:
      location_command(subparsers)

      if type not in ('builtin',):
        put_command(subparsers)
        get_command(subparsers)
  
    return subparsers

  @abc.abstractmethod
  def add_commands(self, parser):
    '''Adds commands to a given (argparse) parser.
    
    This method, effectively, allows you to define special commands that your
    database will be able to perform when called from the common driver like
    for example ``create`` or ``checkfiles``.
    
    You are not obliged to overwrite this method. If you do, you will have the
    chance to establish your own commands. You don't have to worry about stock
    commands such as ``put``, ``get``, ``location`` or ``version``. They will
    be automatically hooked-in depending on the values you return for
    ``type()`` and ``files()``.

    Keyword arguments

    parser
      An instance of a argparse.Parser that you can customize, i.e., call
      ``add_argument()`` on.
    '''
    return
