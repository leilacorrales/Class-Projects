
import re
import json

from mrjob.job import MRJob

QUALITY_RE = re.compile(r"[01459]")

class WindDirection(MRJob):

    def mapper(self, _, line):
        val = line.strip()

        (temp, tq, wind_dir, wq) = (val[87:92], val[92:93], val[60:63], val[63:64])

        # we want direction as key, we want weather data --> temperature
        # want: low, high, count
        # group all with same direction

        # "valid" directions and temps
        if (
            temp != "+9999"
            and wind_dir != "999"
            and re.match(QUALITY_RE, tq)
            and re.match(QUALITY_RE, wq) ):  
            yield wind_dir, {"temp":temp, "count":1}
            # key              value
            # if: yield key, {values}


<<<<<<< HEAD
=======

>>>>>>> 97fabd369b783af71b127897429de445337a1390
    def reducer(self, key, values):
        #  the reducer will find the min max total. from group -> single line per direction
        count = 0
        low = None
        high = None

        for v in values:
            temp1 = v["temp"]

            if low is None:
                low = temp1
            else: 
                low = min(low, temp1)

            if high is None:
                high = temp1
            else: 
                high = max(high, temp1)

            count = count + 1
<<<<<<< HEAD
=======
            
        yield key, {"low": low, "high": high, "count": count}
>>>>>>> 97fabd369b783af71b127897429de445337a1390

if __name__ == '__main__':
    WindDirection.run()
