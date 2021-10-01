from colors import *
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image
from wordcloud import WordCloud
import constants
import json
import os
import random
import re

class Monitor:
  def __init__(self, width, height):
    self.width = width
    self.height = height

class Configuration:
  def __init__(self, monitor_width, monitor_height, wordcloud_background, wordcloud_margin):
    self.monitorWidth = monitor_width
    self.monitorHeight = monitor_height
    self.wordcloudBackground = wordcloud_background
    self.wordcloudMargin = wordcloud_margin

def getProcessList():
  processList = []

  with open(constants.TOP_OUTPUT, 'r') as topFile:
    topOutput = topFile.read().split('\n')[7:]

    for line in topOutput[:-1]:
      line = re.sub(r'\s+', ' ', line).strip()
      fields = line.split(' ')

      try:
        if fields[11].count('/') > 0:
          process = fields[11].split('/')[0]
        else:
          process = fields[11]

        cpu = float(fields[8].replace(',', '.'))
        mem = float(fields[9].replace(',', '.'))

        if process != 'top':
          processList.append((process, cpu, mem))
      except:
        pass

  return processList

def getProcessDictionary(process_list):
  processDictionary = {}

  for process, cpu, mem in process_list:
    if process in processDictionary:
      processDictionary[process][0] += cpu
      processDictionary[process][1] += mem
    else:
      processDictionary[process] = [cpu + 1, mem + 1]

  return processDictionary

def getResourseDictionary(process_list):
  processDictionary = getProcessDictionary(process_list)

  resourceDictionary = {}
  for process, [cpu, mem] in processDictionary.items():
    resourceDictionary[process] = (cpu ** 2 + mem ** 2) ** 0.5

  return resourceDictionary

def getMonitorDimensions(configuration):
  try:
    width, height = ((os.popen("xrandr | grep '*'").read()).split()[0]).split('x')

    return Monitor(int(width), int(height))
  except:
    pass

    return Monitor(configuration.monitorWidth, configuration.monitorHeight)

def getConfiguration():
  configJSON = json.loads(open(constants.CONFIGURATION_FILE, 'r').read())

  return Configuration(configJSON['resolution']['width'], configJSON['resolution']['height'], configJSON['wordcloud']['background'], configJSON['wordcloud']['margin'])

def generateWallpaper(configuration, monitor, resource_dictionary, color_map):
  wordCloud = WordCloud(
    background_color = configuration.wordcloudBackground,
    width = monitor.width - 2 * int(configuration.wordcloudMargin),
    height = monitor.height - 2 * int(configuration.wordcloudMargin),
    colormap = colorMap
  ).generate_from_frequencies(resourceDictionary)

  wordCloud.to_file(constants.WORD_CLOUD_IMAGE_NAME)

  wordCloudImage = Image.open(constants.WORD_CLOUD_IMAGE_NAME)
  wallpaperImage = Image.new(constants.IMAGE_MODE, (monitor.width, monitor.height), configuration.wordcloudBackground)
  wallpaperImage.paste(
    wordCloudImage,
    (
      configuration.wordcloudMargin,
      configuration.wordcloudMargin
    )
  )
  wallpaperImage.save(constants.WALLPAPER_IMAGE_NAME)

configuration = getConfiguration()
monitor = getMonitorDimensions(configuration)
processList = getProcessList()
resourceDictionary = getResourseDictionary(processList)
colorMap = LinearSegmentedColormap.from_list(constants.COLOR_MAP_NAME, colors[random.randint(1, len(colors))])
generateWallpaper(configuration, monitor, resourceDictionary, colorMap)
