
import re
import json

from mrjob.job import MRJob

# NAME = re.compile()
# DATA Line: A,K,923
# Columns ares first entry, Rows are third entry

class rowcol2(MRJob):

    def mapper(self, _, line):
        val = line.strip()
        
        (col,row,entry) = (val[0:1],val[2:3],val[4:8])
        entry = int(entry)
        row = str(row)
        col = str(col)

        yield col, {"type":"column", "sub":row, "entry":entry, "count":1}
            # if: yield key, {values}
        yield row, {"type":"row", "sub":col, "entry":entry, "count":1}
            # if: yield key, {values}

        # print(val,entry,col)

    def reducer(self, key, values):
        col0 = []
        row0 = []
        colsub = []
        rowsub = []
      
        for value in values:
            if value["type"] == "column":
                col0.append(value["entry"])
                row01 = value["sub"]
                colsub.append(row01)
                # yield key, {"value":value["entry"], "example":row01}
            else:
                row0.append(value["entry"])
                col01 = value["sub"]
                rowsub.append(col01)
                # yield key, {"value":value["entry"], "example":col01}

        if len(col0) > 0:
            maxcol = max(col0)
            idx = col0.index(maxcol)
            yield key, {"value":maxcol, "example":colsub[idx]}
        if len(row0) > 0:
            minrow = min(row0)
            idx = row0.index(minrow)
            yield key, {"value":minrow, "example":rowsub[idx]}
            
if __name__ == '__main__':
    rowcol2.run()
