/**
* @file
* 
* @copyright Copyright (c) 2020 Western Digital Corporation or its affiliates,
*                          Arseniy Aharonov <arseniy@aharonov.icu>
* 
* @project   STAT-Framework
* @date      September 01, 2018
* @brief     Implements a simple set of unit-tests for STAT-Mock to emulate 
*            conditions of user-like tests
*******************************************************************************/

/******************************************************************************/
/*     INCLUDE FILES                                                          */
/******************************************************************************/
#include "stat.h"
#include "stat_i.h"

/******************************************************************************/
/*     DEFINITIONS                                                            */
/******************************************************************************/
#undef D_CURRENT_FILE
#define D_CURRENT_FILE _USER_LIKE_TESTS_C

/******************************************************************************/
/*     MACROS                                                                 */
/******************************************************************************/

/******************************************************************************/
/*     TYPES                                                                  */
/******************************************************************************/

/******************************************************************************/
/*     LOCAL PROTOTYPES                                                       */
/******************************************************************************/

// Unit-tests
static void Test_TestGetCallDetails(void);

// Helper fucntions
static void Test_VerifyCallDetailsBeforeActualCalls(const _UU32 mocksCount);
static void Test_VerifyCallDetailsAfterActualCalls(const _UU32 *data_p, const _UU32 mocksCount);

/******************************************************************************/
/*     EXTERNAL PROTOTYPES                                                    */
/******************************************************************************/

/******************************************************************************/
/*     GLOBAL VARIABLES                                                       */
/******************************************************************************/

/******************************************************************************/
/*     START IMPLEMENTATION                                                   */
/******************************************************************************/

_UU32 Test_RunMockUserLikeTests(void)
{
  UNITY_BEGIN();
  Stat_SetTestSetupTeardownHandlers(Stat_SetupMock, 0);
  RUN_TEST(Test_TestGetCallDetails);
  return UNITY_END();
}

static void Test_TestGetCallDetails(void)
{
  _UU32 index;
  _UU32 data[] = {0xAAAAAAAAUL, 0xBBBBBBBBUL, 0, 0xCCCCCCCCUL, 0xDDDDDDDDUL};
  const _UU32 mocksCount = STAT_ARRAY_LEN(data);

  STAT_ADD_NUMERIC_MOCK(Test_TestAddMock, Stat_Rand());
  for (index = 0; index < mocksCount; index++)
  {
    STAT_ADD_NUMERIC_MOCK(Test_TestGetMockHandle, Stat_Rand());
  }

  Test_VerifyCallDetailsBeforeActualCalls(mocksCount);
  
  STAT_POP_MOCK_WITH_SPYING_NUMERIC(Test_TestAddMock, Stat_Rand());
  for (index = 0; index < mocksCount; index++)
  {
    if (data[index])
    {
      STAT_POP_MOCK_WITH_SPYING_NUMERIC(Test_TestGetMockHandle, data[index]);
    }
    else
    {
      STAT_POP_MOCK(Test_TestGetMockHandle);
    }
  }
  
  Test_VerifyCallDetailsAfterActualCalls(data, mocksCount);
}

static void Test_VerifyCallDetailsBeforeActualCalls(const _UU32 mocksCount)
{
  _UU32 index;

  TEST_ASSERT_EQUAL(0, STAT_GET_CALL_ORDER(Test_TestAddMock, 0));
  TEST_ASSERT_NULL(STAT_GET_MOCK_SPY_DATA(Test_TestAddMock, 0));
  
  TEST_ASSERT_EQUAL(0, STAT_COUNT_CALLS(Test_TestAddMock));
  TEST_ASSERT_EQUAL(0, STAT_COUNT_CALLS(Test_TestGetMockHandle));  
  for (index = 0; index < mocksCount; index++)
  {
    TEST_ASSERT_EQUAL(0, STAT_GET_CALL_ORDER(Test_TestGetMockHandle, index));
    TEST_ASSERT_NULL(STAT_GET_MOCK_SPY_DATA(Test_TestGetMockHandle, index));
  }
}

static void Test_VerifyCallDetailsAfterActualCalls(const _UU32 *data_p, const _UU32 mocksCount)
{
  _UU32 index;
  
  TEST_ASSERT_EQUAL(1, STAT_COUNT_CALLS(Test_TestAddMock));
  TEST_ASSERT_EQUAL(mocksCount, STAT_COUNT_CALLS(Test_TestGetMockHandle));
  
  TEST_ASSERT_NOT_NULL(STAT_GET_MOCK_SPY_DATA(Test_TestAddMock, 0));
  TEST_ASSERT_EQUAL(1, STAT_GET_CALL_ORDER(Test_TestAddMock, 0));
  for (index = 0; index < mocksCount; index++)
  {
    TEST_ASSERT_EQUAL(index + 2, STAT_GET_CALL_ORDER(Test_TestGetMockHandle, index));
    if (data_p[index])
    {
      TEST_ASSERT_EQUAL_HEX(data_p[index], *(_UU32*)(STAT_GET_MOCK_SPY_DATA(Test_TestGetMockHandle, index)));
    }
    else
    {
      TEST_ASSERT_NULL(STAT_GET_MOCK_SPY_DATA(Test_TestGetMockHandle, index));
    }
  }
  TEST_ASSERT_EQUAL(1, STAT_GET_CALL_ORDER(Test_TestAddMock, 0));
}

/******************************************************************************/
/*     END OF FILE                                                            */
/******************************************************************************/


