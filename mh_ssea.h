/*! \file mh_ssea.h 
	\brief A steady state EA with elitism. */ 

#ifndef MH_SSEA_H
#define MH_SSEA_H

#include "mh_advbase.h"
#include "mh_param.h"

/** \ingroup param 
Don't count duplicates as generation. If this parameter is set, the
generation counter for the statistics is not incremented for created
duplicates in a steady-state EA. */
extern bool_param dcdag;

/** \ingroup param 
Mutation probability for chromosomes that were not created via
recombination. The normal pmut is used for chromosomes created via
recombination. If pmutnc=0, the value of pmut is adopted.
See pmut, respectively the method chromosome::mutation(double) for the 
exact meaning of negative mutation rates.
If pmutnc<-1000, the value (pmutnc-1000) is also used as average
probability, but at least one mutation is applied, so that no chromosome
is simply copied. */
extern double_param pmutnc;

/** A Steady-State EA.
	During each generation, only one new solution is generated by means
	of variation operators (crossover and mutation). The new solution
	replaces an existing solution (e.g. the worst of the population).
	Usually, generated duplicates discarded ("duplicate elimination"). */ 
class steadyStateEA : public mh_advbase
{
public:
	/** The constructor.
		An initialized population already containing chromosomes 
		must be given. Note that the population is NOT owned by the 
		EA and will not be deleted by its destructor. */
	steadyStateEA(pop_base &p, const pstring &pg=(pstring)("")) : mh_advbase(p,pg) {};
	/** Another constructor.
		Creates an empty EA that can only be used as a template. */
	steadyStateEA(const pstring &pg=(pstring)("")) : mh_advbase(pg) {};
	/** Create new steadyStateGA.
		Returns a pointer to a new steadyStateEA. */
	mh_advbase *clone(pop_base &p,const pstring &pg=(pstring)(""))
	    { return new steadyStateEA(p,pg); }
	/** Performs a single generation. */
	void performGeneration();
	/** The selection function.
		Calls a concrete selection technique and returns the index
		of the selected chromosome in the population. */
	virtual int select()
		{ nSelections++; return tournamentSelection(); }
};

#endif //MH_SSEA_H
