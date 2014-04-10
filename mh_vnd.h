/*! \file mh_vnd.h
A general class Variable Neighborhood Descent VND.
*/

#ifndef MH_VND_H
#define MH_VND_H

#include "mh_lsbase.h"
#include "mh_param.h"

/** \ingroup param
    If set logging is performed in VND. */
extern bool_param vndlog;

/** \ingroup param
    Maximum number of VND neighborhood to be used (0,...,vndnum()). */
extern int_param vndnum;

/** \ingroup param
    VND neighborhood ordering:
    - 0: static
    - 1: random
    - 2: adaptive */
extern int_param vndorder;


/** A class for diverse strategies to change the order of the neighborhood
 * structures within VND, VNS etc. */
class NBStructureOrder
{
protected:
	/** Number of neighborhood structures. */
	int lmax;
	/** The actual order of the neighborhood structures.
	 * first is the index of the neighborhood structure,
	 * second a priority value for adaptive strategies whose
	 * meaning depends on the specific strategy. */
	vector<pair<int,double> > order;
	/** The strategy for adapting the order:
	 * - 0: static first to last
	 * - 1: random order
	 * - 2: adaptive */
	int strategy;
	/// Permutes the order randomly
	void permuteRandomly();
public:
	/** Initialized object for lmax neighborhood structures. */
	NBStructureOrder(int _lmax,int _strategy=0);
	/** Destructor. */
	virtual ~NBStructureOrder()
	{ }
	/** Get the i-th neighborhood. */
	int get(int i)
	{ return order[i].first; }
	/** Calculate a new ordering. */
	void calculateNewOrder();
};


/** An abstract interface class for solutions
    used in a VND heuristic. */
class VNDProvider
{
public:
	/// Virtual destructor.
	virtual ~VNDProvider() {};
	
	/** Searches neighborhood l (in 1..getVNDNNum) of
	    the current solution
	    and changes the current solution to the best found. */
	virtual void searchVNDNeighborhood(int l) = 0;

	/// Returns the number of neighborhood structures available
	virtual int getVNDNNum() = 0;
	/** Returns the number of neighborhood structures to be used,
	    considering vndnum(). */
	int get_lmax(const pstring &pg);
};


class VNDStatAggregator;


/** VND base class, implementing the variable neighborhood descent.
Not only looking for a possible improvement in one neighborhood, but in
several different ones.  The chromosome for this algorithm has implement
the VNDProvider interface.  */
class VND : public lsbase
{
	friend class VNDStatAggregator;
protected:
	int l; ///< number of current neighborhood structure
	int lmax;			///< total number of neighborhoods
	vector<int> nSearch;		///< number of searching calls
	vector<int> nSearchSuccess;	///< number of successful searches
	vector<double> sumSearchGain;	///< total gain achieved
	vector<double> time;	///< total CPU-time used by the NB search
	NBStructureOrder *nborder; ///< neighborhood order
	bool own_nborder; ///< true if the VND created its own NBStructureOrder
public:
	/** The constructor.
		An initialized population already containing chromosomes 
		must be given. Note that the population is NOT owned by the 
		algorithm and will not be deleted by its destructor. VND
		will only use the first chromosome. 
		If no NBStructureOrder object is provided, the VND creates
		its own static one. */
	VND(pop_base &p, const pstring &pg=(pstring)(""), NBStructureOrder *nbo=NULL);
	/** The destructor. */
	virtual ~VND() 
	{
		if (own_nborder)
			delete nborder;
	}
	/** Run the VND algorithm */
	virtual void run();
	/** Performs a single generation.
		Is called from run() */
	virtual void performGeneration();
	/** Write only meaningful information into log. */
	virtual void writeLogHeader();
	/** Write only meaningful information into log. */
	virtual void writeLogEntry(bool inAnyCase = false);
	/** Write detailed statistics on searched neighborhoods. */
	void printStatisticsVND(ostream &ostr);
	/** General print Statistics method extended. */
	void printStatistics(ostream &ostr);
};


/** A class for aggregating the neighborhood statistics information
    on multiple VND runs. */
class VNDStatAggregator
{
public:
	int lmax;			///< total number of neighborhoods
	vector<int> nSearch;		///< number of searching calls
	vector<int> nSearchSuccess;	///< number of successful searches
	vector<double> sumSearchGain;	///< total gain achieved
	vector<double> time;	///< total CPU-time
	int vndCalls;			///< total number of VND calls

	/** Initialization with number of neighborhoods. */
	VNDStatAggregator(int lmax);
	/** Add statistics of VND object. */
	void add(const VND &vnd);
	/** Write detailed statistics on searched neighborhoods. */
	void printStatisticsVND(ostream &ostr);
};



#endif //MH_VND_H
