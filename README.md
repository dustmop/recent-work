# recent-work

Looks at your local git repos, finds the commits from the last few days, and displays them in a compact form.

## configuration

Create a file called `.recent-work.json` in your home directory. Its contents should be JSON of a list of directories, like this:

```
[
  "~/code/my-projects/",
  "~/code/tools/",
  "~/job/"
]
```

Currently, this script will look one level deep to find git repos. So, for example, it would find git projects located at:

```
~/code/my-projects/cool-thing/.git

~/code/my-project/another-repo/.git

~/code/tools/recent-work/.git

~/job/something/.git
```

## command-line

Once the config file exists, simply invoke:

```
python recent-work.py
```

Arguments:

```
 -n [days]  Number of days to look back (default 5)
```
