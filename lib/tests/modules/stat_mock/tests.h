/**
* @file
* 
* @copyright Copyright (c) 2020 Western Digital Corporation or its affiliates,
*                          Arseniy Aharonov <Arseniy.Aharonov@gmail.com>
* 
* @project   STAT-Framework
* @date      September 01, 2018
* @brief     Declares definitions, types and prototypes for the unit-tests of 
*            STAT-Mock feature
*******************************************************************************/


#ifndef _TESTS
#define _TESTS
/******************************************************************************/
/*     INCLUDE FILES                                                          */
/******************************************************************************/
#include <unity.h>

/******************************************************************************/
/*     DEFINITIONS                                                            */
/******************************************************************************/
#undef D_CURRENT_FILE
#define D_CURRENT_FILE _TESTS_H

/******************************************************************************/
/*     MACROS                                                                 */
/******************************************************************************/

/******************************************************************************/
/*     TYPES                                                                  */
/******************************************************************************/

/******************************************************************************/
/*     EXPORTED GLOBALS                                                       */
/******************************************************************************/

/******************************************************************************/
/*     FUNCTION PROTOTYPES                                                    */
/******************************************************************************/

_UU32 Test_RunMockMainTests(void);
_UU32 Test_RunMockUserLikeTests(void);

#endif /* This is actually EOF */

