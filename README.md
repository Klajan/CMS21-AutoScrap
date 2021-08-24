
# CMS 2021 Auto Scrap

Automates the process of scraping parts using pattern matching




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
python script.py
```
### Now works with any 16:9 resolution

Tested from 720p to 1440p!

## Known Bugs

#### It does not hit the perfect bonus every time

Yes, unfortunatly, to solve this issue we would need to have more iteration of the program per second but I don't know how to optimize this code

Multithreading did improve performance up to 40% but it can still miss on rare ocasions and slower computers.

*Further improvent could be done with a better algothrithm*

#### Might rarely not scrap item

I didn't manage to figre out why, if it happens scraping the current item and starting a new one should fix this

## Contributing

Contributions are always welcome!

Message me on instagram or twitter @mauvbeats

  
## Authors

- [@xelag](https://www.github.com/xelag)
- [Klajan](https://github.com/Klajan)
  