# list-mbed-platforms
Simple script to list Mbed platforms from os.mbed.com

### Example of usage

- Help

```
python list-platforms.py -h
```

- Filter by vendor

```
python list-platforms.py -v ST
```

- Filter by vendor

```
python list-platforms.py -p ST
```

- Check externa file

```
python list-platforms.py -f file.txt
```

Note: if no file is specified, the application will attemp to read from the confluence page

#### Configuration to read from Confluence

Create a `.env` file and add the following:

```
CONFLUENCE_USER=<your user>
CONFLUENCE_PASS=<your pass>
```