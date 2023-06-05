# CMS 2021 Auto Scrap

Automates the process of scraping or repairing parts using pattern matching

## Installation

### Exe

 1. Extract Zip
 2. Launch AutoScrap.exe

### Script

Here is the list of dependencies
 - Python >= 3.7
 - Numpy
 - OpenCV2
 - MSS
 - PyInput
To install dependencies use the following command:
```bash
pip install -r requirements.txt
```
To launch the script use the following command:
```bash
python AutoScrap.py
```

### Settings

Monitor number can be set in settings.json. Default: 1
**Works with any 16:9 resolution**

## Known Bugs

#### It does not hit the perfect bonus every time

**Hopefully fixed**
While grabbing the screenshot still takes 6ms the improved algorithm reduced the template matching time from 9ms to 0.6ms.

## Building using pyinstaller

To build using pyinstaller >= 5.11
```bash
pyinstaller .\AutoScrap.spec
```

## Contributing

Contributions are always welcome!
Message me on instagram or twitter @mauvbeats

## Authors

- [@xelag](https://www.github.com/xelag)
- [Klajan](https://www.github.com/Klajan)
