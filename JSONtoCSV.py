import pandas as pd

df = pd.read_json("filehere.json")
#df.to_excel("newexcelfile.xlsx")
#df.to_csv("newcsvfile.csv")

#data cleaning -- add column to substring
def addcolumn(r):
  locationColumn = r["location"] #look for column that have sub json string
  print(locationColumn["latitude"]) #check type
  if type(locationColumn) == dict:
    r["lat"] = locationColumn["latitude"] #add column named "lat"
    r["long"] = locationCoumn["longtitude"] #add column named "long"
  else:
    r["lat"] = None
    r["long"] = None
  return r

ndf = df.apply(addcolumn,axis=1) #apply this function to every row (axis=1)

ndf.to_excel("newexcel.xlsx")
ndf.to_csv("newcsv.csv")