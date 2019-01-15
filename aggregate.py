#!/usr/bin/python3
"""Calculate grouped basic statistics for one or two tsv-files obtained e.g. by
mhlib's summary.py.

The input data are either given via stdin or in one or two files provided 
as parameters. If two tsv files are given, they are assumed to be results
from two different algorithms on the same instances, and they are compared
including a Wilcoxon rank sum test.

Important: For the aggregation to work correctly, adapt in particular
below definitions of categ, categ2 and categbase according to your
conventions for the filenames encoding instance and run information.

Consider this script more as an example or template. 
"""

import pandas as pd
import numpy as np
import scipy.stats
import sys
import re
import warnings
import argparse
import math


#--------------------------------------------------------------------------------
def categ(x):
    """Determine the category name to aggregate over from the given file name.
    
    For aggregating a single table of raw data,  
    return category name for a given file name.
    """
    # re.sub(r"^(.*)/(T.*)-(.*)_(.*).res",r"\1/\2-\3",x)
    return re.sub(r".*[lcs|lcps]_(\d+)_(\d+)_(\d+)\.(\d+)(\.out)", 
        r"\1/\2-\3",x)
    #return re.sub(r"([^/#_]*)(_.*_)?([^/#_]*)(__\d+)?([^/#_]*)\.out",
    #    r"\1\3\5",x)

def categ2(x):
    """For aggregating two tables corresponding to two different summary files,
    extract category name from the given file names that shall be compared.
    """
    # re.sub(r"^(.*)/(T.*)-(.*)_(.*).res",r"\2-\3")
    return re.sub(r"^.*[lcs|lcps]_(\d+)_(\d+)_(\d+)\.(\d+)(\.out)",
           r"\1/\2-\3",x)
    #return re.sub(r"^.*/([^/#_]*)(_.*_)?([^/#_]*)(#\d+)?([^/#_]*)\.out",
    #       r"\1\2\3\4\5",x)

def categbase(x):
    """For aggregating two tables corresponding to two different 
    configurations that shall be compared, return detailed name of run 
    (basename) that should match a corresponding one of the other configuration.
    """
    #re.sub(r"^.*/(T.*)-(.*)_(.*).res",r"\1-\2-\3",x)
    return re.sub(r"^.*[lcs|lcps]_(\d+)_(\d+)_(\d+)\.(\d+)(\.out)",
           r"\1_\2_\3.\4\5",x)
    #return re.sub(r"^.*/([^/#_]*)(_.*_)?([^/#_]*)(#\\d+)?([^/#_]*)\\.out",
    #       r"\1_\2_\3.\4\5",x)
       
# Set display options for output
pd.options.display.width = 10000
pd.options.display.max_rows = None
pd.options.display.precision = 8
#pd.set_eng_float_format(accuracy=8)

#--------------------------------------------------------------------------------
# General helper functions

def geometric_mean(x,shift=0):
    """Calculates geometric mean with shift parameter
    """
    return math.exp(math.mean(math.log(x+shift)))-shift   

def calculateObj(rawdata,args):
    if args.times:
        return (rawdata["obj"] == rawdata["UB"]) * rawdata["ttot"] + (
                rawdata["obj"] != rawdata["UB"]) * 100000000
    else:
        return rawdata["obj"]

#-------------------------------------------------------------------------
# Aggregation of one summary data frame

def aggregate(rawdata,categfactor=categ):
    """Determine aggregated results for one summary data frame.
    """
    rawdata["cat"]=rawdata.apply(lambda row: categfactor(row["file"]),axis=1)
    rawdata["gap"]=rawdata.apply(lambda row: (row["ub"]-row["obj"])/row["ub"],axis=1)
    grp = rawdata.groupby("cat")
    aggregated = grp.agg({"obj":[size,mean,std],
                          "ittot":median, "ttot":median, "ub":mean,
                          "gap":mean, "tbest":median})[["obj","ittot","ttot","ub"]]
    return aggregated
    #aggregated = pd.DataFrame({"runs":grp["obj"].size(),
    #                           "obj_mean":grp["obj"].mean(),
    #                           "obj_sd":grp["obj"].std(),
    #                           "ittot_med":grp["ittot"].median(),
    #                           "ttot_med":grp["ttot"].median(),
    #                           "ub_mean":grp["ub"].mean(),
    #                           "gap_mean":grp["gap"].mean(),
    #                           "tbest_med":grp["tbest"].median(),
    #                           # "tbest_sd":grp["tbest"].std(),
    #                           })
    #return aggregated[["runs","obj_mean","obj_sd","ittot_med","ttot_med",
    #                   "ub_mean","gap_mean","tbest_med"]]
    
def aggregatemip(rawdata,categfactor=categ):
    """Determine aggregated results for one summary data frame for MIP results.
    """
    rawdata["cat"]=rawdata.apply(lambda row: categfactor(row["file"]),axis=1)
    rawdata["gap"]=rawdata.apply(lambda row: (row["Upper_bound"]-
           row["Lower_bound"])/row["Upper_bound"],axis=1)
    grp = rawdata.groupby("cat")
    aggregated = pd.DataFrame({"runs":grp["obj"].size(),
                               "ub_mean":grp["Upper_bound"].mean(),
                               "ub_sd":grp["Upper_bound"].std(),
                               "lb_mean":grp["Lower_bound"].mean(),
                               "lb_sd":grp["Lower_bound"].std(),
                               "ttot_med":grp["ttot"].median(),
                               "gap_mean":grp["gap"].mean(),
                               # "tbest_med":grp["tbest"].med(),
                               # "tbest_sd":grp["tbest"].std(),
                               })
    return aggregated[["runs","ub_mean","ub_sd","lb_mean","ttot_med","gap_mean"]]

def totalagg(agg):
    """Calculate total values over aggregate data.
    """
    total = pd.DataFrame({"total":[""],
               "runs":[agg["runs"].sum()],
               "obj_mean":[agg["obj_mean"].mean()],
               #"obj_sd":agg["obj_sd"].mean(),
               "ittot_med":[agg["ittot_med"].median()],
               "ttot_med":[agg["ttot_med"].median()],
               "tbest_med":[agg["tbest_med"].median()],
               #"tbest_sd":agg["tbest"].std(),
            })
    total = total[["total","runs","obj_mean","ittot_med","ttot_med","ttot_med","tbest_med"]]
    total = total.set_index("total")
    total.index.name = None
    return total

def roundagg(a):
    """Reasonably round aggregated results for printing.
    """
    return a.round({'obj_mean':6, 'obj_sd':6, 'ittot_med':1, 'itbest_med':1,
        'ttot_med':1, 'tbest_med':1, 'obj0_mean':6, 'obj1_mean':6})

def roundaggmip(a):
    """Reasonably round aggregated MIP results for printing.
    """
    return a.round({'ub_mean':6, 'ub_sd':6, 'lb_mean':6, 'lb_sd':6, 'ttot_med':1,
                    'gap_mean':1})

def agg_print(rawdata):
    """Perform aggregation and print results for one summary data frame.
    """
    aggregated = aggregate(rawdata)
    aggtotal = totalagg(aggregated)
    print(roundagg(aggregated))
    print("\nTotals:")
    print(roundagg(aggtotal))


#-------------------------------------------------------------------------
# Aggregation and comparison of two summary data frames


def stattest(col1,col2):
    """Perform one-sided statistical test (Wilcoxon signed rank-test)
for the assumption col1<col2.
    """
    dif = col1 - col2
    noties = len(dif[dif != 0])
    med_is_less = np.median(dif) < 0
    if noties<1:
        return float(1)
    # if (col1==col2).all():
    #     return 3
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        msr,p = scipy.stats.wilcoxon(col1,col2,correction=True,zero_method="wilcox")
    #s,p = scipy.stats.mannwhitneyu(col1,col2,alternative="less")
    p = p/2
    if not med_is_less:
        p = 1 - p
    return p

def doaggregate2(raw,fact):
    """Aggregate results of two merged summary data frames.
    """
    raw["obj_diff"]=raw.apply(lambda row: row["obj_x"]-row["obj_y"],axis=1)
    raw["AlessB"]=raw.apply(lambda row: row["obj_x"]<row["obj_y"],axis=1)
    raw["BlessA"]=raw.apply(lambda row: row["obj_x"]>row["obj_y"],axis=1)
    raw["AeqB"]=raw.apply(lambda row: row["obj_x"]==row["obj_y"],axis=1)
    # rawdata["gap"]=raw.apply(lambda row: (row["ub"]-row["obj"])/row["ub"],axis=1)
    grp = raw.groupby(fact)
    p_AlessB={}
    p_BlessA={}
    for g,d in grp:
        p_AlessB[g] = stattest(d["obj_x"],d["obj_y"])
        p_BlessA[g] = stattest(d["obj_y"],d["obj_x"])
    aggregated = pd.DataFrame({"runs":grp["obj_x"].size(),
                               "A_obj_mean":grp["obj_x"].mean(),
                               "B_obj_mean":grp["obj_y"].mean(),
                               "diffobj_mean":grp["obj_diff"].mean(),
                               "AlessB":grp["AlessB"].sum(),
                               "BlessA":grp["BlessA"].sum(),
                               "AeqB":grp["AeqB"].sum(),
                               "p_AlessB":p_AlessB,
                               "p_BlessA":p_BlessA,
                            })
    return aggregated[["runs","A_obj_mean","B_obj_mean","AlessB","BlessA",
                      "AeqB","p_AlessB","p_BlessA"]]
    
def aggregate2(rawdata1,rawdata2):
    """Determine aggregated results for two summarry data frames including comparison of results.
    """
    rawdata1["base"]=rawdata1.apply(lambda row: categbase(row["file"]),axis=1)
    rawdata2["base"]=rawdata2.apply(lambda row: categbase(row["file"]),axis=1)
    raw = pd.merge(rawdata1,rawdata2,on="base",how="outer")
    raw["class"]=raw.apply(lambda row: categ2(row["file_x"]),axis=1)
    aggregated = doaggregate2(raw,"class")
    raw["total"]=raw.apply(lambda row: "total",axis=1)
    aggtotal = doaggregate2(raw,"total")
    return {"grouped":aggregated,"total":aggtotal}

def roundagg2(a):
    """Rounds aggregated data for two summary data frames for printing.
    """
    a["AlessB"] = a["AlessB"].map(lambda x: int(x))
    a["BlessA"] = a["BlessA"].map(lambda x: int(x))
    a["AeqB"] = a["AeqB"].map(lambda x: int(x))
    a = a.round({"A_obj_mean":6, "B_obj_mean":6, "diffobj_mean":6, 
                    "AlessB":0, "BlessA":0, "AeqB":0, "p_AlessB":4, "p_BlessA":4})
    return a
    
def printsigdiffs(agg2):
    """Print signifficant differences in aggregated data for two summary 
    data frames.
    """
    Awinner = sum(agg2["AlessB"]>agg2["BlessA"])
    Bwinner = sum(agg2["AlessB"]<agg2["BlessA"])
    gr = agg2["AlessB"].size
    print("A is yielding more frequently better results on ", Awinner,
          " groups (",round(Awinner/gr*100,2),"%)") 
    print("B is yielding more frequently better results on ", Bwinner, 
          " groups (",round(Bwinner/gr*100,2),"%)") 
    print("\nSignificant differences:")
    sigAlessB = agg2[agg2.p_AlessB<=0.05] 
    sigBlessA = agg2[agg2.p_BlessA<=0.05] 
    if not sigAlessB.empty:
        print("\np_AlessB<=0.05\n",sigAlessB)
    if not sigBlessA.empty:
        print("\np_BlessA<=0.05\n",sigBlessA)         

def agg2_print(rawdata1,rawdata2):
    """Perform aggregation and print comparative results for two summary 
    data frames.
    """
    aggregated = aggregate2(rawdata1,rawdata2)
    print(roundagg2(pd.concat([aggregated["grouped"],aggregated["total"]])))
    #print(roundagg2(aggregated["total"]))
    print("")
    printsigdiffs(roundagg2(pd.concat([aggregated["grouped"],aggregated["total"]])))
    
#-------------------------------------------------------------------------
# main part

# If called as script read one or two summary files or summary data from
# stdin, aggregate, and print.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate aggregated statistics for one or two summary files obtained from summary.py")
    parser.add_argument('-t', '--times', action="store_true", default=False,
        help='Consider total times for proven optimal solutions (10000000 if no opt prove)')
    parser.add_argument("file", nargs="?", help="File from summary.py to be aggregated")
    parser.add_argument("file2", nargs="?", help="Second file from summary.py to be aggregated and compared to")
    args = parser.parse_args()
    
    print(args.file2);
    
    if not args.file2:
        # process one summary file
        f = args.file if args.file else sys.stdin 
        rawdata = pd.read_csv(f, sep='\t')
        rawdata["obj"] = calculateObj(rawdata,args)
        agg_print(rawdata)
    else:
        # process and compare two summary files
        rawdata1 = pd.read_csv(args.file, sep='\t')
        rawdata1["obj"] = calculateObj(rawdata1,args)
        rawdata2 = pd.read_csv(args.file2, sep='\t')
        rawdata2["obj"] = calculateObj(rawdata2,args)
        agg2_print(rawdata1,rawdata2) 

