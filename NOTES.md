# Random

```

# convert images and add a gray shadow:
# zmniejsz_ramka.sh

convert xxx.png \( -clone 0 -background gray -shadow 80x3+10+10 \) \( -clone 0 -background gray -shadow 80x3-5-5 \) -reverse -background white -layers merge -resize 600 out.jpg

# autopep8
autopep8 --in-place --aggressive filename.py
```



# MLRPT - meteor decoder

- decoder webpage: http://5b4az.org/
- tested for `mlrpt-1.1`, next versions: 1.2, 1.3 - I was unable to compile on my system (Debian like - tips needed)
- compilation:

```
cd ~/Downloads/
tar jxvf mlrpt-1.1.tar.bz2
cd mlrpt-1.1
./autogen.sh
#./configure
./configure CFLAGS="-g -O2"
make -j4
sudo make install
```
- images will go to `/home/user/mlrpt/` - edit `/home/user/mlrpt/mlrptrc` for fine tuning

- `autowx2_conf.py` entry:

```
'METEOR-M2': {
		'freq': '137900000',    # not so important, as mlrpt uses its own fixed value
		'processWith': 'modules/meteor-m2/meteor.sh',
		'priority': 1},
```



# errors

/usr/local/lib/python2.7/dist-packages/matplotlib/pyplot.py:524: RuntimeWarning: More than 20 figures have been opened. Figures created through the pyplot interface (`matplotlib.pyplot.figure`) are retained until explicitly closed and may consume too much memory. (To control this warning, see the rcParam `figure.max_open_warning`).
  max_open_warning, RuntimeWarning)


	plt.close()?
