
import re
import json

from mrjob.job import MRJob

# NAME = re.compile()
# DATA Line: A,K,923
# Columns ares first entry, Rows are third entry

class rowcol3(MRJob):

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
        col0 = []   # all values
        row0 = []
        colsub = [] # all rows/cols from each value
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

        # function: input max or min value, output list of indices
        def maxminindex(zero,zero0):
            indices = []
            for i in range(len(zero0)):
                if zero0[i] == zero:
                    indices.append(i)
            return indices            

        # function: input list of indices --> output values from another lsit of the indices
        def listlist(ids,ids0):
            colsub0 = []
            for i in ids:
                colsub0.append(ids0[i])
            return colsub0            

        # run function within a function

        if len(col0) > 0:
            maxcol = max(col0)
            idx = listlist(maxminindex(maxcol,col0),colsub)
            yield key, {"value":maxcol, "example":idx}
        if len(row0) > 0:
            minrow = min(row0)
            idx = listlist(maxminindex(minrow,row0),rowsub)
            yield key, {"value":minrow, "example":idx}
            
if __name__ == '__main__':
    rowcol3.run()
