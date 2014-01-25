import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas import Series, DataFrame
import KNGLib as k

sf = k.SF('prd')
ms = k.MSSQL('prd')

print "Fired up k.SF as sf, so sf.do_query('SELECT Something')"
print "Fired up k.MSSQL as ms, ms.do_query('SELECT SOMETHING')"
print "Send alerts with k.alert('lee@kng.com','some subject','something happened') "
print "This is PRD by the way"
