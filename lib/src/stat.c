/**
* @file
* 
* @copyright Copyright (c) 2020 Western Digital Corporation or its affiliates,
*                          Arseniy Aharonov <arseniy@aharonov.icu>
*            SPDX-License-Identifier: MIT
* 
* @project   STAT Framework
* @date      July 31, 2016
* @brief     Implements common functionality if the STAT framework
*******************************************************************************/

/******************************************************************************/
/*     INCLUDE FILES                                                          */
/******************************************************************************/
#include <unity.h>
#include "stat.h"
#include "stat_i.h"

/******************************************************************************/
/*     DEFINITIONS                                                            */
/******************************************************************************/

/******************************************************************************/
/*     MACROS                                                                 */
/******************************************************************************/

/******************************************************************************/
/*     TYPES                                                                  */
/******************************************************************************/

/******************************************************************************/
/*     LOCAL PROTOTYPES                                                       */
/******************************************************************************/
static void Stat_DummyHandler(void);

/******************************************************************************/
/*     EXTERNAL PROTOTYPES                                                    */
/******************************************************************************/

/******************************************************************************/
/*     GLOBAL VARIABLES                                                       */
/******************************************************************************/
STAT_HANDLER Stat_setupHandler = Stat_DummyHandler;
STAT_HANDLER Stat_teardownHandler = Stat_DummyHandler;

/******************************************************************************/
/*     START IMPLEMENTATION                                                   */
/******************************************************************************/

/**
* The main routine of the STAT framework
*
* @return the status reported by the Unity harness
*/
int main(void)
{
  return Stat_Main();
}

/**
* Initializes the "test-setup" and the "test-tear-down" handlers that are 
* called at the beginning and at the end of each test accordingly
*
* @param setupHandler - a handler for test setup (if NULL - no action on test 
*                       setup)
* @param teardownHandler - a handler for test tear-down (if NULL - no action on 
*                          test tear-down)
*
* @return None
*/
void Stat_SetTestSetupTeardownHandlers(STAT_HANDLER setupHandler, STAT_HANDLER teardownHandler)
{
  Stat_setupHandler = (setupHandler)? setupHandler: Stat_DummyHandler;
  Stat_teardownHandler = (teardownHandler)? teardownHandler: Stat_DummyHandler;
}

/* A dummy handler for the test setup/tear-down handlers */
static void Stat_DummyHandler(void)
{
}

/* Unity standard setup routine */
void setUp(void)
{
  Stat_InitRng();
#ifdef STAT_MOCK
  Stat_SetupMock();
#endif
#ifdef STAT_PRODUCT_SETUP
  Stat_SetupProductTest();
#endif
  Stat_setupHandler();
}

/* Unity standard tear-down routine */
void tearDown(void)
{
  Stat_teardownHandler();
#ifdef STAT_PRODUCT_TEARDOWN
  Stat_TeardownProductTest();
#endif
#ifdef STAT_MOCK
  Stat_TearDownMock();
#endif
}

void Stat_Memcpy(void *target_p, const void *source_p, _UU32 size)
{
  _UU8 *nextTarget_p = (_UU8*)target_p + size;
  const _UU8 *nextSource_p = (_UU8*)source_p + size;

  while ((_UU8*)target_p < nextTarget_p--)
  {
    *nextTarget_p = *(--nextSource_p);
  }
}

void Stat_Memset(void *target_p, _UU32 value, _UU32 size)
{
  _UU8 *next_p = ((_UU8*)target_p) + size;
  
  while ((_UU8*)target_p < next_p--)
  {
    *next_p = (_UU8)value;
  }
}

_UU32 Stat_AreStringsEqual(const char *first_p, const char *second_p)
{
  const char *charA_p = first_p;
  const char *charB_p = second_p;

  if (!charA_p || !charB_p)
  {
    return (charA_p == charB_p);
  }

  while (*charA_p || *charB_p)
  {
    if (*charA_p++ != *charB_p++)
    {
      return 0;
    }
  }

  return !0;
}

/******************************************************************************/
/**    END OF FILE                                                           **/
/******************************************************************************/

