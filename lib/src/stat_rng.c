/**
* @file
* 
* @copyright Copyright (c) 2020 Western Digital Corporation or its affiliates,
*                          Arseniy Aharonov <arseniy@aharonov.icu>
*            SPDX-License-Identifier: MIT
*
* @project   STAT Framework
* @date      July 31, 2016
* @brief     Implements Random-Number generation functionality
*******************************************************************************/

/******************************************************************************/
/*     INCLUDE FILES                                                          */
/******************************************************************************/
#include <unity.h>
#include <stat.h>
#include <stat_i.h>

/******************************************************************************/
/*     DEFINITIONS                                                            */
/******************************************************************************/

/* Random-Number generator definitions (please, do not change it) */
#define D_STAT_RNG_DEFAULT_SEED   (0x12345678)

/******************************************************************************/
/*     MACROS                                                                 */
/******************************************************************************/

/******************************************************************************/
/*     TYPES                                                                  */
/******************************************************************************/

/******************************************************************************/
/*     LOCAL PROTOTYPES                                                       */
/******************************************************************************/
static _UU32 Stat_ApplyMixJenkins32(_UU32 value);

/******************************************************************************/
/*     EXTERNAL PROTOTYPES                                                    */
/******************************************************************************/

/******************************************************************************/
/*     GLOBAL VARIABLES                                                       */
/******************************************************************************/
_UU32 Stat_rngRandomSeeds[D_STAT_RNG_SOURCE_TOTAL_COUNT] = {0};

/******************************************************************************/
/*     START IMPLEMENTATION                                                   */
/******************************************************************************/

/**
* Initializes the RNG engine
*
* @return None
*/
void Stat_InitRng(void)
{
  _UU32 seedId;
  for (seedId = 0; seedId < D_STAT_RNG_SOURCE_TOTAL_COUNT; seedId++)
  {
    Stat_rngRandomSeeds[seedId] = D_STAT_RNG_DEFAULT_SEED;
  }
}
 
/**
* Generates a random number using the specified RNG source
*
* @param sourceId - the Id of the RNG source
* @return the generated value
*/
_UU32 Stat_RandBySource(_UU32 sourceId)
{
  _UU32 seed = Stat_rngRandomSeeds[sourceId];

  /** Calculate a new seed and a value **/
  seed = Stat_ApplyMixJenkins32(seed);
  if (seed == 0)
  {
    seed = 1;
  }
  Stat_rngRandomSeeds[sourceId] = seed;
  
  return (seed - 1);
}

/**
* Picks a random number within the specified range using the specified RNG 
* source
*
* @param range_max - maximal value of the range
* @param range_min - minimal value of the range
* @param sourceId - the ID of the RNG source
* @return the randomly picked number
*/
_UU32 Stat_RandRangeBySource(_UU32 sourceId, _UU32 rangeMin, _UU32 rangeMax)
{
   _UU32 randValue = Stat_RandBySource(sourceId);
   _UU32 range = rangeMax - rangeMin + 1;
   if (range)
   {
      randValue = (randValue/range) + (randValue % range);
      randValue = (randValue % range) + rangeMin;
   }
   return randValue;
}

/**
* Generates a random number
*
* @return the generated value
*/
_UU32 Stat_Rand(void)
{
  return Stat_RandBySource(D_STAT_RNG_SOURCE_DEFAULT);
}

/**
* Picks a random number within the specified range 
* 
* @param range_max - maximal value of the range
* @param range_min - minimal value of the range
* @return the randomly picked number
*/
_UU32 Stat_RandRange(_UU32 rangeMin, _UU32 rangeMax)
{
  return Stat_RandRangeBySource(D_STAT_RNG_SOURCE_DEFAULT, rangeMin, rangeMax);
}

/**
* Selects a next unique pseudo-random number within the range based on the      
* previous given choice
*
* @param previouseSelection - the previously selected random from this range
* @param rangeMax - the maximal number in the range
* @param rangeMin - the minimal number in the range
* @return the selected new unique random value
* @remarks This function works only for ranges lesser then 
*          D_STAT_LARGEST_32BIT_PRIME
*/
_UU32 Stat_SelectNextUniqueRandInRange(_UU32 rangeMin, _UU32 rangeMax, _UU32 previouseSelection)
{
  _UU32 range;
  _UU32 nextSelection;

  range = rangeMax - rangeMin + 1;
  nextSelection = (previouseSelection - rangeMin);
  nextSelection = nextSelection + ((STAT_LARGEST_32BIT_PRIME) % range);
  nextSelection = (nextSelection % range) + rangeMin;

  return nextSelection;
}

/**
* Fills the given buffer with random data
*
* @param buffer_p - the buffer to fill
* @param size - the size of the buffer
* @return None
*/
void Stat_FillBufferWithRandom(void* buffer_p, _UU32 size)
{
  _UU8 *bytes_p = (void*)buffer_p;
  _UU32 byteCount = size;
  while (byteCount--)
  {
    *bytes_p++ = (_UU8)Stat_Rand();
  }
}

/**
* Fills the given buffer with non-zero byts of random data
*
* @param buffer_p - the buffer to fill
* @param size - the size of the buffer
* @return None
*/
void Stat_FillWithNonZeroRandomBytes(void* buffer_p, _UU32 size)
{
  _UU8 *bytes_p = (void*)buffer_p;
  _UU8 randValue;
  _UU32 byteCount = size;
  while (byteCount--)
  {
    randValue = (_UU8)Stat_Rand();
    randValue = (randValue)? randValue: (_UU8)Stat_Rand();
    *bytes_p++ = randValue;
  }
}

/* Applies the Mix-Jenkins32 to the specified _UU32 value */
static _UU32 Stat_ApplyMixJenkins32(_UU32 value)
{
  _UU32 result = value;
  result += (result << 12);
  result ^= (result >> 22);
  result += (result << 4);
  result ^= (result >> 9);
  result += (result << 10);
  result ^= (result >> 2);
  result += (result << 7);
  result ^= (result >> 12);
  return result;
}

/******************************************************************************/
/*     END OF FILE                                                            */
/******************************************************************************/


