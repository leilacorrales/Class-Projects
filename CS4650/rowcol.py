
import re
import json

from mrjob.job import MRJob

# NAME = re.compile()
# DATA Line: A,K,923
# Columns ares first entry, Rows are third entry

class rowcol(MRJob):

    def mapper(self, _, line):
        val = line.strip()
        
        (col,row,entry) = (val[0:1],val[2:3],val[4:8])
        entry = int(entry)

        yield col, {"type":"column", "entry":entry, "count":1}
            # if: yield key, {values}
        yield row, {"type":"row", "entry":entry, "count":1}
            # if: yield key, {values}

        # print(val,entry,col)

    def reducer(self, key, values):
        col0 = []
        row0 = []
      
        for value in values:
            if value["type"] == "column":
                col0.append(value["entry"])
                # yield key, value["entry"]
            else:
                row0.append(value["entry"])
                # yield key, value["entry"]

        if len(col0) > 0:
            maxcol = max(col0)
            yield key, maxcol
        if len(row0) > 0:
            minrow = min(row0)
            yield key, minrow
            
if __name__ == '__main__':
    rowcol.run()
