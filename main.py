import datetime
import json
import os
import subprocess


def read_file(filename):
  fp = open(filename, 'r')
  content = fp.read()
  fp.close()
  return content


class FileEnt(object):
  def __init__(self, dir, basename):
    self.dir = dir
    self.basename = basename
    self.fullpath = os.path.join(dir, basename)
    ts = os.path.getmtime(self.fullpath)
    self.mtime = datetime.datetime.fromtimestamp(ts)
    self.isdir = os.path.isdir(self.fullpath)

  def __repr__(self):
    year = self.mtime.year
    month = self.mtime.month
    day = self.mtime.day
    return '#<FileEnt "%s" %04d-%02d-%02d>' % (self.basename, year, month, day)


class Commit(object):
  def __init__(self, id, date_text, message):
    self.id = id
    self.date_text = date_text
    self.message = shorten(message, 32)

  def __repr__(self):
    sha = self.id[0:6]
    return '#<Commit %s "%s" @ %s>' % (sha, self.message, self.date_text)


def shorten(text, size):
  if len(text) < size:
    return text
  return text[:size-3] + '...'


def parse_time_text(text):
  text = text[:len(text)-6]
  dt = datetime.datetime.strptime(text, '%a %b %d %H:%M:%S %Y')
  return dt


def is_old_event(dt):
  delta = datetime.datetime.now() - dt
  return delta > datetime.timedelta(days=5)


def is_old_folder(folder):
  delta = datetime.datetime.now() - folder.mtime
  return delta > datetime.timedelta(weeks=1)


def list_entities(dirpath):
  dirpath = dirpath.replace('~', os.environ['HOME'])
  ents = os.listdir(dirpath)
  res = []
  for ent in ents:
    try:
      res.append(FileEnt(dirpath, ent))
    except FileNotFoundError:
      continue
  res.sort(key=lambda f: f.mtime)
  res.reverse()
  return res


def fetch_param(text, prefix, capture):
  if text.startswith(prefix):
    capture.clear()
    capture.append(text[len(prefix):].strip())
    return True
  return False


def get_recent_commits(folder):
  cwd = os.getcwd()
  os.chdir(folder.fullpath)
  cmd = ['git', 'log', '-n', '10']
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  # TODO: check return code
  content = p.communicate()[0]
  os.chdir(cwd)
  content = str(content, 'utf-8')

  res = []
  commit_id = None
  when = None
  message = None
  done = False
  capture = []
  for line in content.split('\n'):
    if fetch_param(line, 'commit ', capture):
      done = False
      commit_id = capture[0]
      continue
    if fetch_param(line, 'Merge: ', capture):
      continue
    if fetch_param(line, 'Author: ', capture):
      continue
    if fetch_param(line, 'Date: ', capture):
      when = parse_time_text(capture[0])
      if is_old_event(when):
        break
      continue
    if not line:
      continue
    if not done:
      done = True
      message = line.strip()
      res.append(Commit(commit_id, when, message))
  return res


def find_recent_work(dirpath):
  folders = list_entities(dirpath)
  for folder in folders:
    if not folder.isdir:
      continue
    if is_old_folder(folder):
      break
    commits = get_recent_commits(folder)
    if not len(commits):
      continue
    print(folder)
    for c in commits:
      print(c)
    print('')


def main():
  roots = json.loads(read_file('roots.json'))
  for root in roots:
    find_recent_work(root)


if __name__ == '__main__':
  main()
