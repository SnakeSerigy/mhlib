// mh_simanneal.C

#include <cmath>
#include "mh_random.h"
#include "mh_simanneal.h"
#include "mh_util.h"
#include "mh_gaopsprov.h"

namespace mh {

/// Cooling slope
double_param saca( "saca", "slope for geometric cooling", 0.95, 1.0, UPPER );

/// Cooling interval
int_param sacint( "sacint", "interval between cooling steps", 1, 1, LOWER_EQUAL );

/// Initial temperature
double_param satemp( "satemp", "initial temperature for simulated annealing", 1.0, 0.0, LOWER );

simulatedAnnealing::simulatedAnnealing(pop_base &p, const std::string &pg) : lsbase(p,pg)
{
	T = satemp(pgroup);
}

void simulatedAnnealing::performIteration()
{
	checkPopulation();

	perfIterBeginCallback();

	mh_solution *pold=pop->at(0);
	tmpSol->copy(*pold);
	gaopsProvider::cast(*tmpSol).selectNeighbour();

	if (tmpSol->isBetter(*pold))
		tmpSol=replace(tmpSol);
	else
		if ( accept( pold, tmpSol ) )
		{
			tmpSol=replace(tmpSol);
			nDeteriorations++;
		}

	cooling();

	nIteration++;

	perfIterEndCallback();
}

void simulatedAnnealing::cooling()
{
	// Geometric cooling.
	if ( ( nIteration % sacint(pgroup) ) == 0 )
		T *= saca(pgroup);
}

bool simulatedAnnealing::accept( mh_solution *o, mh_solution *n )
{
	/// Metropolis criterion.
	return random_prob( exp( -fabs( ( n->obj() - o->obj() ) / T ) ) );
}

} // end of namespace mh

