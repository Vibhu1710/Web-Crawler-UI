# common imports
import numpy as np
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import continuityManager as cm

import database.LocalDataBaseMonitor as ldb
import database.RDSMonitor as rds
import database.ExtractedDataMonitor as extractManager

# set the tableMap
rds.tableMap = rds.getTableToColumnsMap()

# chrome driver path
PATH = r"crawler_scripts/chromedriver.exe"
