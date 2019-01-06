# Random

```

# convert images and add a gray shadow:
convert xxx.png \( -clone 0 -background gray -shadow 80x3+10+10 \) \( -clone 0 -background gray -shadow 80x3-5-5 \) -reverse -background white -layers merge out.jpg


```

# MLRPT - meteor decoder

- http://5b4az.org/

```
cd ~/Downloads/
tar jxvf mlrpt-1.1.tar.bz2
cd mlrpt-1.1
./autogen.sh
./configure
make -j4
sudo make install
```
