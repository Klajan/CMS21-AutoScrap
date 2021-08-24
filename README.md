
# CMS 2021 Auto Scrap

Automates the process of scraping or repairing parts using pattern matching




## Installation

Here is the list of dependency

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
### Now works with any 16:9 resolution

Tested from 720p to 1440p!

## Known Bugs

#### It does not hit the perfect bonus every time
**Hopefully fixed**

While grabbing the screenshot still takes 6ms the improved algorithm reduced the template matching time from 9ms to 0.6ms.

#### Might rarely not scrap item
**Fixed**

Limiting the search to red channel only should prevent matches not happening

## Contributing

Contributions are always welcome!

Message me on instagram or twitter @mauvbeats

  
## Authors

- [@xelag](https://www.github.com/xelag)
- [Klajan](https://www.github.com/Klajan)
  