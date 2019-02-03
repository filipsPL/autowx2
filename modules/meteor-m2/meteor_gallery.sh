#!/bin/bash

#
# moving recorded images to the appropriate final dir
#

# value for some tests:
# fileNameCore="20190118-1012_METEOR-M2"
# rawImageDir="./"



outHtml="$imgdir/$fileNameCore.html"  # html for this single pass
indexHtml="$imgdir/index.html"        # main index file for a given day
htmlTemplate="$wwwDir/index.tpl"


# ---single gallery preparation------------------------------------------------#

makethumb() {
    obrazek="$1"
    local thumbnail=$(basename "$obrazek" .jpg)".th.jpg"
    convert -define jpeg:size=200x200 "$obrazek" -thumbnail '200x200^' granite: +swap -gravity center -extent 200x200 -composite -quality 82 "$thumbnail"
    echo "$thumbnail"
    }

# -----------------------------------------------------------------------------#

logFile="$imgdir/$fileNameCore.log"   # log file to read from

varDate=$(sed '1q;d' $logFile)
varSat=$(sed '3q;d' $logFile)
varStart=$(sed '4q;d' $logFile) # unused
varDur=$(sed '5q;d' $logFile)
varPeak=$(sed '6q;d' $logFile)
varFreq=$(sed '7q;d' $logFile)

dateTime=$(date -d @$varStart +"%Y-%m-%d")
dateTimeDir=$(date -d @$varStart +"%Y/%m/%d")  # directory format of date, eg. 2018/11/22/
wwwPath=$wwwRootPath/recordings/meteor/img/$dateTimeDir




# -----------------------------------------------------------------------------#


cd $rawImageDir

if [ $(ls *.jpg 2> /dev/null | wc -l) = 0 ];
then
  echo "no images";
else

  #
  # should we resize images?
  #

  if [ "$resizeimageto" != "" ]; then
    echo "Resizing images to $resizeimageto px"
    mogrify -resize ${resizeimageto}x${resizeimageto}\> *.jpg
  fi

  #
  # some headers
  #

  echo "<h2>$varSat | $varDate</h2>" > $outHtml
  echo "<p>f=${varFreq}Hz, peak: ${varPeak}°, duration: ${varDur}s</p>" >> $outHtml

  #
  # loop over images and generate thumbnails
  #



  for obrazek in *.jpg
  do
  		echo "Thumb for $obrazek"
  		# base=$(basename $obrazek .jpg)
      sizeof=$(du -sh "$obrazek" | cut -f 1)
      # generate thumbnail
      thumbnail=$(makethumb "$obrazek")
  		echo $thumbnail
      echo "<a data-fancybox='gallery' data-caption='$varSat | $varDate ($sizeof)' href='$wwwPath/$obrazek'><img src='$wwwPath/$thumbnail' alt='meteor image' title='$sizeof' class='img-thumbnail' /></a> " >> $outHtml
  done


  #
  # get image core name
  #

  meteorcorename=$(ls *.jpg | head -1 | cut -d "-" -f 1-2)
  echo $wwwPath/$meteorcorename > $wwwDir/meteor-last-recording.tmp

  #
  # move images to their destination
  #

  mv $rawImageDir/* $imgdir/
  # cp $rawImageDir/* $imgdir/


  # ----consolidate data from the given day ------------------------------------#
  # generates neither headers nor footer of the html file

  echo "" > $indexHtml.tmp
  for htmlfile in $(ls $imgdir/*.html | grep -v "index.html")
  do
    cat $htmlfile >> $indexHtml.tmp
  done

  # ---------- generates pages according to the template file -------------------

  currentDate=$(date)
  echo $currentDate

  export htmlTitle="METEOR-M2 images | $dateTime"
  export htmlBody=$(cat $indexHtml.tmp)

  source $htmlTemplate > $indexHtml

  #
  # generate static main page(s)
  #

  $baseDir/bin/gen-static-page.sh


fi # there are images
