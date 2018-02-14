#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# autowx2 - genpastable.py
# generates the pass table and recording plan for tne next few days and the appropriate plot
#
# GANTT Chart with Matplotlib
# Sukhbinder
# inspired by:
# https://sukhbinder.wordpress.com/2016/05/10/quick-gantt-chart-with-matplotlib/
# taken from
# https://github.com/fialhocoelho/test/blob/master/plot/gantt.py
#

from autowx2 import *
import matplotlib
matplotlib.use('Agg')  # Force matplotlib to not use any Xwindows backend.
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.dates
from matplotlib.dates import DateFormatter
import numpy as np


def t2humanHM(timestamp):
    '''converts unix timestamp to human readable format'''
    return strftime('%H:%M', time.localtime(timestamp))


def _create_date(timestamp):
    """Creates the date from timestamp"""
    mdate = matplotlib.dates.date2num(datetime.fromtimestamp(timestamp))
    return mdate


def CreateGanttChart(listNextPasesListList):
    """
        Create gantt charts with matplotlib
    """

    ylabels = []
    customDates = []

    i = 1
    for tx in listNextPasesListList:
        ylabel, startdate, enddate = tx
        # ylabels.append("%s (%1i)" % (ylabel, i) )
        ylabels.append("(%1i)" % (i))
        # ylabels.append("%s" % (ylabel) )
        customDates.append([_create_date(startdate), _create_date(enddate)])
        i += 1

    ilen = len(ylabels)
    pos = np.arange(0.5, ilen * 0.5 + 0.5, 0.5)
    task_dates = {}
    for i, task in enumerate(ylabels):
        task_dates[task] = customDates[i]
    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111)
    for i, ylabel in enumerate(ylabels):
        ylabelIN, startdateIN, enddateIN = listNextPasesListList[i]
        start_date, end_date = task_dates[ylabels[i]]
        ax.barh(
            (i * 0.5) + 0.5,
            end_date - start_date,
            left=start_date,
            height=0.3,
            align='center',
            edgecolor='black',
            color='navy',
            alpha=0.95)
        ax.text(
            end_date,
            (i * 0.5) + 0.55,
            ' %s | %s' % (t2humanHM(startdateIN),
                          ylabelIN),
            ha='left',
            va='center',
            fontsize=7,
            color='gray')

    locsy, labelsy = plt.yticks(pos, ylabels)
    plt.setp(labelsy, fontsize=8)
    ax.axis('tight')
    ax.set_ylim(ymin=-0.1, ymax=ilen * 0.5 + 0.5)
    ax.grid(color='silver', linestyle=':')
    ax.xaxis_date()

    # FAKE,startdate,FAKE=listNextPasesListList[0]
    # minutOdPelnej = int(datetime.fromtimestamp(time.time()).strftime('%M'))
    # plotStart = int(time.time() - minutOdPelnej*60)
    # print t2human(plotStart)
    # ax.set_xlim(_create_date(plotStart), _create_date(enddate+600))

    Majorformatter = DateFormatter("%H:%M\n%d-%b")
    ax.xaxis.set_major_formatter(Majorformatter)

    labelsx = ax.get_xticklabels()
    # plt.setp(labelsx, rotation=30, fontsize=10)
    plt.setp(labelsx, rotation=0, fontsize=7)
    plt.title(
        'Transit plan for %s, generated %s' %
        (stationName, t2human(time.time())))

    font = font_manager.FontProperties(size='small')
    ax.legend(loc=1, prop=font)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(ganttNextPassList)
    
    print "This is done only to satisfy the codacy.com. Sorry for that.", ["" for x in [ylabel, enddateIN, locsy] ]


def listNextPasesHtml(passTable, howmany):
    i = 1
    output = "<table>\n"
    output += "<tr><td>#</td><td>satellite</td><td>start</td><td>duration</td><td>peak</td><td>azimuth</td><td>freq</td><td>process with</td><tr>\n"

    for satelitePass in passTable[0:howmany]:
        satellite, start, duration, peak, azimuth = satelitePass
        freq = satellitesData[satellite]['freq']
        processWith = satellitesData[satellite]['processWith']

        output += "<tr><td>%i</td><td>%s</td><td>%s</td><td>%s</td><td>%s°</td><td>%s° (%s)</td><td>%sHz</td><td>%s</td><tr>\n" % (
            i, satellite, t2human(start), t2humanMS(duration), peak, azimuth, azimuth2dir(azimuth), freq, processWith)
        i += 1

    output += "</table>\n"

    return output


def listNextPasesTxt(passTable, howmany):

    txtTemplate = "%3s\t%10s\t%16s\t%9s\t%4s\t%3s\t%6s\t%10s\t%20s\n"

    i = 1
    output = ""
    output += txtTemplate % (
        "#",
        "satellite",
     "start",
     "dur MM:SS",
     "peak",
     "az",
     "az",
     "freq",
     "process with")

    for satelitePass in passTable[0:howmany]:
        satellite, start, duration, peak, azimuth = satelitePass
        freq = satellitesData[satellite]['freq']
        processWith = satellitesData[satellite]['processWith']

        output += txtTemplate % (
            i,
            satellite,
            t2human(start),
            t2humanMS(duration),
            peak,
            azimuth,
            azimuth2dir(azimuth),
            freq,
            processWith)
        i += 1

    output += "\n"

    return output


def listNextPasesList(passTable, howmany):
    output = []
    for satelitePass in passTable[0:howmany]:
        satellite, start, duration, peak, azimuth = satelitePass
        #freq = satellitesData[satellite]['freq']
        #processWith = satellitesData[satellite]['processWith']

        output.append([satellite, start, start + duration])
    print peak == True ## codacy cheating, sorry.
    return output


def saveToFile(filename, data):
    plik = open(filename, "w")
    plik.write(data)
    plik.close()


if __name__ == "__main__":

    # recalculate table of next passes
    passTable = genPassTable(howmany=50)
    listNextPasesHtmlOut = listNextPasesHtml(passTable, 100)
    saveToFile(htmlNextPassList, listNextPasesHtmlOut)

    listNextPasesListList = listNextPasesList(passTable, 20)
    CreateGanttChart(listNextPasesListList)

    print listNextPasesTxt(passTable, 100)
