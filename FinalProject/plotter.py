import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import datetime

multiple_bars = plt.figure()

x = [1, 2, 3, 4]
x1 = [1.1, 2.1, 3.1, 4.1]

y = [4, 9, 2, 5]
z = [1, 2, 3, 5]
k = [11, 12, 13, 5]

ax = plt.subplot(111)
b1 = ax.bar(x, y, width=0.1, color='b', align='center')
b2 = ax.bar(x1, z, width=0.1, color='g', align='center')
b3 = ax.bar(x, k, width=0.1, color='r', align='center')

plt.legend((b1,b2,b3),('fuck','shit','murder'))
plt.show()
