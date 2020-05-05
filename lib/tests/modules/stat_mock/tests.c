/**
* @file
* 
* @copyright Copyright (c) 2020 Western Digital Corporation or its affiliates,
*                          Arseniy Aharonov <Arseniy.Aharonov@gmail.com>
*
* @project   STAT Framework
* @date      February 21, 2017
* @brief     Implements an unit-tests for the callmock module of STAT
*******************************************************************************/

/******************************************************************************/
/*     INCLUDE FILES                                                          */
/******************************************************************************/
#include "stat.h"
#include "stat_i.h"
#include "stat_mock_i.h"
#include "tests.h"

/******************************************************************************/
/*     DEFINITIONS                                                            */
/******************************************************************************/

/******************************************************************************/
/*     MACROS                                                                 */
/******************************************************************************/

#ifndef STAT_MOCK_PERMISSIVE_VALIDATION
#define TEST_ABORT_UPON_NON_STAT_MOCK_PERMISSIVE_VALIDATION() \
  TEST_IGNORE_MESSAGE("Test completes only in the permissive-validation mode!");
#else
#define TEST_ABORT_UPON_NON_STAT_MOCK_PERMISSIVE_VALIDATION()
#endif

/******************************************************************************/
/*     TYPES                                                                  */
/******************************************************************************/

typedef struct _TestCallbackSpy
{
  _UU32 callCount;
  _UU32 callOrder;
  const void* mock_p;
  const void *dataToSpy_p;
}_TestCallbackSpy_t;

typedef struct _TestStatMock
{
  _TestCallbackSpy_t callbackA;
  _TestCallbackSpy_t callbackB;
  _TestCallbackSpy_t overrideHandler;
}_TestStatMock_t;

typedef struct _TestMockOject
{
  _UU32 firstValue;
  _UU32 secondValue;
}_TestMockOject_t;

/******************************************************************************/
/*     LOCAL PROTOTYPES                                                       */
/******************************************************************************/

// Unit-tests
static void Test_TestMockInitialization(void);
static void Test_TestAddMock(void);
static void Test_TestMultipleAddMocks(void);
static void Test_TestAddMocksWithDifferentSizes(void);
static void Test_TestAddMocksForDifferentDeclarators(void);
static void Test_TestMocksWithCallbacks(void);
static void Test_TestPopMockWithSpying(void);
static void Test_TestPopMocksWithSpyingAndCallbacks(void);
static void Test_TestAddEmptyMock(void);
static void Test_TestAddCallbackMock(void);
static void Test_TestAddManyMocks(void);
static void Test_TestSpyingAfterAddMultipleMocks(void);
static void Test_TestCallbackUponAddMultipleMocks(void);
static void Test_TestGetMockHandle(void);
static void Test_TestSpyOn(void);
static void Test_TestMultipleSpyOn(void);
static void Test_TestCountCallables(void);
static void Test_TestCountCalls(void);
static void Test_TestHasMocks(void);
static void Test_TestHasUnconsumedMocks(void);
static void Test_TestFindUnconsumedMock(void);
static void Test_TestMockTeardown(void);
static void Test_TestAddMockNoOverflow(void);
static void Test_TestAddMockWithOverflow(void);
static void Test_TestPopMockWithSpyNoOverflow(void);
static void Test_TestPopMockWithSpyWithOverflow(void);
static void Test_TestSpyOnWithoutOverflow(void);
static void Test_TestSpyOnWithOverflow(void);
static void Test_TestGetSpyDataOutOfBound(void);
static void Test_TestGetCallOrderDataOutOfBound(void);
static void Test_TestCallOrderBeyondNaturalLimitForSpys(void);
static void Test_TestCallOrderBeyondNaturalLimitForMocks(void);
static void Test_TestCallOrderTrackingUponNoViolation(void);
static void Test_TestCallOrderTrackingUponOrderViolation(void);
static void Test_TestSingleCallToOverriddenMock(void);
static void Test_TestMultipleCallToOverriddenMock(void);
static void Test_TestAddReusableMockForSingleUse(void);
static void Test_TestAddNumericReusableMock(void);
static void Test_TestSpiedDataUponReusableMock(void);
static void Test_TestStatisticsUponReusableMock(void);
static void Test_TestMixedWithReusableMocks(void);
static void Test_TestCallbackUponReusableMock(void);
static void Test_TestReusableEmptyMock(void);
static void Test_TestReusableMockOverConsumption(void);
static void Test_TestReusableMockWithOverflowDueToDataSizeInconsistency(void);
static void Test_TestNonExistingSpyDataExtractionUponReusableMock(void);
static void Test_TestAddInfiniteMockUponSingleUse(void);
static void Test_TestAddInfiniteMockUponSeveralUses(void);
static void Test_TestAddNumericInfiniteMock(void);
static void Test_TestSpiedDataUponInfiniteMock(void);
static void Test_TestStatisticsUponInfiniteMock(void);
static void Test_TestInfiniteEmptyMock(void);
static void Test_TestInfiniteCallbackMock(void);

// Helper fucntions
static void Test_SetupTest(void);
static void Test_TearDownTest(void);
static void Test_HandleMockCallbackA(_UU32 callOrder, void* mock_p, void* dataToSpy_p);
static void Test_HandleMockCallbackB(_UU32 callOrder, void* mock_p, void* dataToSpy_p);
static void Test_SpyOnTestCallbackCall(_UU32 callOrder, void* mock_p, void* dataToSpy_p, _TestCallbackSpy_t *spy_p);
static void Test_EnforceCallOrderTracking(_UU32 callOrder, void* mock_p, void* dataToSpy_p);
static void Test_CeaseCallOrderTracking(_UU32 callOrder, void* mock_p, void* dataToSpy_p);
static void* Test_OverrideMock(_UU32 callOrder, _UU32 callCount, const void* dataToSpy_p);

/******************************************************************************/
/*     EXTERNAL PROTOTYPES                                                    */
/******************************************************************************/

/******************************************************************************/
/*     GLOBAL VARIABLES                                                       */
/******************************************************************************/
_TestStatMock_t Test_statMock;

/******************************************************************************/
/*     START IMPLEMENTATION                                                   */
/******************************************************************************/

_UU32 Stat_Main(void)
{
  _UU32 status = 0;
  status |= Test_RunMockMainTests();
  status |= Test_RunMockUserLikeTests();
  return status;
}

_UU32 Test_RunMockMainTests(void)
{
  UNITY_BEGIN();
  RUN_TEST(Test_TestMockInitialization);
  Stat_SetTestSetupTeardownHandlers(Test_SetupTest, Test_TearDownTest);
  RUN_TEST(Test_TestAddMock);
  RUN_TEST(Test_TestMultipleAddMocks);
  RUN_TEST(Test_TestAddMocksWithDifferentSizes);
  RUN_TEST(Test_TestAddMocksForDifferentDeclarators);
  RUN_TEST(Test_TestMocksWithCallbacks);
  RUN_TEST(Test_TestPopMockWithSpying);
  RUN_TEST(Test_TestPopMocksWithSpyingAndCallbacks);
  RUN_TEST(Test_TestAddEmptyMock);
  RUN_TEST(Test_TestAddCallbackMock);
  RUN_TEST(Test_TestAddManyMocks);
  RUN_TEST(Test_TestSpyingAfterAddMultipleMocks);
  RUN_TEST(Test_TestCallbackUponAddMultipleMocks);
  RUN_TEST(Test_TestGetMockHandle);
  RUN_TEST(Test_TestSpyOn);
  RUN_TEST(Test_TestMultipleSpyOn);
  RUN_TEST(Test_TestCountCallables);
  RUN_TEST(Test_TestCountCalls);
  RUN_TEST(Test_TestHasMocks);
  RUN_TEST(Test_TestHasUnconsumedMocks);
  RUN_TEST(Test_TestFindUnconsumedMock);
  RUN_TEST(Test_TestMockTeardown);
  RUN_TEST(Test_TestAddMockNoOverflow);
  RUN_TEST(Test_TestAddMockWithOverflow);
  RUN_TEST(Test_TestPopMockWithSpyNoOverflow);
  RUN_TEST(Test_TestPopMockWithSpyWithOverflow);
  RUN_TEST(Test_TestSpyOnWithoutOverflow);
  RUN_TEST(Test_TestSpyOnWithOverflow);
  RUN_TEST(Test_TestGetSpyDataOutOfBound);
  RUN_TEST(Test_TestGetCallOrderDataOutOfBound);
  RUN_TEST(Test_TestCallOrderBeyondNaturalLimitForSpys);
  RUN_TEST(Test_TestCallOrderBeyondNaturalLimitForMocks);
  RUN_TEST(Test_TestCallOrderTrackingUponNoViolation);
  RUN_TEST(Test_TestCallOrderTrackingUponOrderViolation);
  RUN_TEST(Test_TestSingleCallToOverriddenMock);
  RUN_TEST(Test_TestMultipleCallToOverriddenMock);
  RUN_TEST(Test_TestAddReusableMockForSingleUse);
  RUN_TEST(Test_TestAddNumericReusableMock);
  RUN_TEST(Test_TestSpiedDataUponReusableMock);
  RUN_TEST(Test_TestStatisticsUponReusableMock);
  RUN_TEST(Test_TestMixedWithReusableMocks);
  RUN_TEST(Test_TestCallbackUponReusableMock);
  RUN_TEST(Test_TestReusableEmptyMock);
  RUN_TEST(Test_TestReusableMockOverConsumption);
  RUN_TEST(Test_TestReusableMockWithOverflowDueToDataSizeInconsistency);
  RUN_TEST(Test_TestNonExistingSpyDataExtractionUponReusableMock);
  RUN_TEST(Test_TestAddInfiniteMockUponSingleUse);
  RUN_TEST(Test_TestAddInfiniteMockUponSeveralUses);
  RUN_TEST(Test_TestAddNumericInfiniteMock);
  RUN_TEST(Test_TestSpiedDataUponInfiniteMock);
  RUN_TEST(Test_TestStatisticsUponInfiniteMock);
  RUN_TEST(Test_TestInfiniteEmptyMock);
  RUN_TEST(Test_TestInfiniteCallbackMock);
  return UNITY_END();
}

static void Test_TestMockInitialization(void)
{
  static _UU8 mock[STAT_MOCK_ALIGNED_SIZE/2 - sizeof(_StatMockBasicEntry_t)];
  static _UU8 data[STAT_MOCK_ALIGNED_SIZE/2];

  Stat_Memset(mock, (_UU32)0xFF, sizeof(mock));
  Stat_Memset(data, (_UU32)0xA5, sizeof(data));

  Stat_SetupMock();
  
  STAT_ADD_MOCK(Test_TestMockInitialization, mock);
  TEST_ASSERT_EQUAL(sizeof(data), Stat_GetMockFreeSpace());
  TEST_ASSERT_EQUAL(0, Stat_CountAllCalls());
  TEST_ASSERT_EQUAL_MEMORY(mock, STAT_GET_MOCK_DATA(Test_TestMockInitialization, 0), sizeof(mock));
  
  STAT_POP_MOCK_WITH_SPYING(Test_TestMockInitialization, data);
  TEST_ASSERT_EQUAL(0, Stat_GetMockFreeSpace());
  TEST_ASSERT_EQUAL(1, Stat_CountAllCalls());
  TEST_ASSERT_EQUAL_MEMORY(data, STAT_GET_MOCK_SPY_DATA(Test_TestMockInitialization, 0), sizeof(data));

  STAT_RESET();
  
  TEST_ASSERT_EQUAL(STAT_MOCK_ALIGNED_SIZE, Stat_GetMockFreeSpace());
  TEST_ASSERT_EQUAL(0, Stat_CountAllCalls());
}

static void Test_TestAddMock(void)
{
  const _UU32 mock = 0xDEADBEEF;
  const _UU32 expectedAllocatedSize = sizeof(_StatMockBasicEntry_t) + sizeof(mock);
  
  STAT_ADD_NUMERIC_MOCK(Test_TestAddMock, mock);

  TEST_ASSERT_EQUAL(STAT_MOCK_ALIGNED_SIZE - expectedAllocatedSize, Stat_GetMockFreeSpace());
  TEST_ASSERT_EQUAL(0, Stat_CountAllCalls());
  
  TEST_ASSERT_NOT_NULL(_STAT_GET_MOCK_HANDLE(Test_TestAddMock, 0));
  TEST_ASSERT_EQUAL(0, STAT_GET_CALL_ORDER(Test_TestAddMock, 0));
  TEST_ASSERT_EQUAL_HEX(mock, *(_UU32*)STAT_GET_MOCK_DATA(Test_TestAddMock, 0));
  TEST_ASSERT_NULL(STAT_GET_MOCK_SPY_DATA(Test_TestAddMock, 0));
  TEST_ASSERT_EQUAL_HEX(mock, *(_UU32*)STAT_POP_MOCK(Test_TestAddMock));
  TEST_ASSERT_NULL(STAT_GET_MOCK_SPY_DATA(Test_TestAddMock, 0));
  TEST_ASSERT_EQUAL(1, STAT_GET_CALL_ORDER(Test_TestAddMock, 0));
}

static void Test_TestMultipleAddMocks(void)
{
  const _UU32 mocks[] = {0xDEADBEEF, 0xFACEACAD, 0xABADFACE};
  const _UU32 mockCount = STAT_ARRAY_LEN(mocks);
  const _UU32 expectedAllocatedSize = sizeof(_StatMockBasicEntry_t) + sizeof(*mocks);
  _UU32 index;

  for (index = 0; index < mockCount; index++)
  {
    STAT_ADD_MOCK(Test_TestMultipleAddMocks, mocks[index]);
  }

  TEST_ASSERT_EQUAL(STAT_MOCK_ALIGNED_SIZE - (expectedAllocatedSize * mockCount),  Stat_GetMockFreeSpace());
  TEST_ASSERT_EQUAL(0, Stat_CountAllCalls());
  
  for (index = 0; index < mockCount; index++)
  {
    TEST_ASSERT_EQUAL(0, STAT_GET_CALL_ORDER(Test_TestMultipleAddMocks, index));
    TEST_ASSERT_EQUAL_HEX(mocks[index], *(_UU32*)STAT_GET_MOCK_DATA(Test_TestMultipleAddMocks, index));
    TEST_ASSERT_EQUAL_HEX(mocks[index], *(_UU32*)STAT_POP_MOCK(Test_TestMultipleAddMocks));
    TEST_ASSERT_EQUAL(index + 1, STAT_GET_CALL_ORDER(Test_TestMultipleAddMocks, index));
    TEST_ASSERT_NULL(STAT_GET_MOCK_SPY_DATA(Test_TestMultipleAddMocks, index));
  }
  
  TEST_ASSERT_EQUAL(mockCount, Stat_CountAllCalls());
}

static void Test_TestAddMocksWithDifferentSizes(void)
{
  const char large[] = "Somewhat long mock!";
  const _UU8 small = 0xA5;
  const _UU8 unaligned[] = {1, 2, 3, 4, 5, 6, 7};
  const _UU32 sizes[] = {STAT_CEILING_ROUND(sizeof(large), STAT_MOCK_MAX_ALIGNMENT), 
    STAT_CEILING_ROUND(sizeof(small), STAT_MOCK_MAX_ALIGNMENT), 
    STAT_CEILING_ROUND(sizeof(unaligned), STAT_MOCK_MAX_ALIGNMENT)};
  const _UU32 totalAllocated = (3 * sizeof(_StatMockBasicEntry_t)) + sizes[0] + sizes[1] + sizes[2];

  STAT_ADD_MOCK(Test_TestAddMocksWithDifferentSizes, large);
  STAT_ADD_MOCK(Test_TestAddMocksWithDifferentSizes, small);
  STAT_ADD_MOCK(Test_TestAddMocksWithDifferentSizes, unaligned);

  TEST_ASSERT_EQUAL(STAT_MOCK_ALIGNED_SIZE - totalAllocated,  Stat_GetMockFreeSpace());

  TEST_ASSERT_EQUAL_STRING(large, STAT_GET_MOCK_DATA(Test_TestAddMocksWithDifferentSizes, 0));
  TEST_ASSERT_EQUAL_STRING(large, STAT_POP_MOCK(Test_TestAddMocksWithDifferentSizes));

  TEST_ASSERT_EQUAL_HEX8_ARRAY(&small, STAT_GET_MOCK_DATA(Test_TestAddMocksWithDifferentSizes, 1), 1);
  TEST_ASSERT_EQUAL_HEX8_ARRAY(&small, STAT_POP_MOCK(Test_TestAddMocksWithDifferentSizes), 1);

  TEST_ASSERT_EQUAL_HEX8_ARRAY(unaligned, STAT_GET_MOCK_DATA(Test_TestAddMocksWithDifferentSizes, 2), 
    sizeof(unaligned));
  TEST_ASSERT_EQUAL_HEX8_ARRAY(unaligned, STAT_POP_MOCK(Test_TestAddMocksWithDifferentSizes), sizeof(unaligned));
}

static void Test_TestAddMocksForDifferentDeclarators(void)
{
  const _UU32 mocks[] = {0xDEADBEEF, 0xFACEACAD, 0xABADFACE};

  STAT_ADD_MOCK(Test_TestAddMocksForDifferentDeclarators, mocks[0]);
  STAT_ADD_MOCK(Test_TestAddMock, mocks[1]);
  STAT_ADD_MOCK(Test_TestMultipleAddMocks, mocks[2]);

  TEST_ASSERT_EQUAL(0, STAT_GET_CALL_ORDER(Test_TestMultipleAddMocks, 0));
  TEST_ASSERT_EQUAL_HEX(mocks[2], *(_UU32*)STAT_GET_MOCK_DATA(Test_TestMultipleAddMocks, 0));
  TEST_ASSERT_EQUAL_HEX(mocks[2], *(_UU32*)STAT_POP_MOCK(Test_TestMultipleAddMocks));
  TEST_ASSERT_EQUAL(1, STAT_GET_CALL_ORDER(Test_TestMultipleAddMocks, 0));

  TEST_ASSERT_EQUAL(0, STAT_GET_CALL_ORDER(Test_TestAddMock, 0));
  TEST_ASSERT_EQUAL_HEX(mocks[1], *(_UU32*)STAT_GET_MOCK_DATA(Test_TestAddMock, 0));
  TEST_ASSERT_EQUAL_HEX(mocks[1], *(_UU32*)STAT_POP_MOCK(Test_TestAddMock));
  TEST_ASSERT_EQUAL(2, STAT_GET_CALL_ORDER(Test_TestAddMock, 0));

  TEST_ASSERT_EQUAL(0, STAT_GET_CALL_ORDER(Test_TestAddMocksForDifferentDeclarators, 0));
  TEST_ASSERT_EQUAL_HEX(mocks[0], *(_UU32*)STAT_GET_MOCK_DATA(Test_TestAddMocksForDifferentDeclarators, 0));
  TEST_ASSERT_EQUAL_HEX(mocks[0], *(_UU32*)STAT_POP_MOCK(Test_TestAddMocksForDifferentDeclarators));
  TEST_ASSERT_EQUAL(3, STAT_GET_CALL_ORDER(Test_TestAddMocksForDifferentDeclarators, 0));
}

static void Test_TestMocksWithCallbacks(void)
{
  _UU32 mocks[] = {0xFACE1111, 0xFACE2222, 0xFACE3333};
  const STAT_MOCK_CALLBACK_T callbacks[] = 
    {Test_HandleMockCallbackA, Test_HandleMockCallbackA, Test_HandleMockCallbackB};
  const _UU32 mockCount = STAT_ARRAY_LEN(mocks);
  const _UU32 expectedAllocatedSize = sizeof(_StatMockBasicEntry_t) + sizeof(*mocks) + sizeof(*callbacks);
  _UU32 *received_p;
  _UU32 index;

  for (index = 0; index < mockCount; index++)
  {
    STAT_ADD_MOCK_WITH_CALLBACK(Test_TestMocksWithCallbacks, mocks[index], callbacks[index]);
  }

  for (index = 0; index < mockCount; index++)
  {
    received_p = STAT_POP_MOCK(Test_TestMocksWithCallbacks);
    TEST_ASSERT_EQUAL_HEX(mocks[index], *received_p);
  }
  
  TEST_ASSERT_EQUAL(STAT_MOCK_ALIGNED_SIZE - (mockCount * expectedAllocatedSize),  Stat_GetMockFreeSpace());
  TEST_ASSERT_EQUAL(2, Test_statMock.callbackA.callCount);
  TEST_ASSERT_EQUAL(1, Test_statMock.callbackB.callCount);
  TEST_ASSERT_EQUAL(2, Test_statMock.callbackA.callOrder);
  TEST_ASSERT_EQUAL(3, Test_statMock.callbackB.callOrder);
  TEST_ASSERT_EQUAL_HEX_ARRAY(&mocks[1],(_UU32*)Test_statMock.callbackA.mock_p, 1);
  TEST_ASSERT_EQUAL_HEX_ARRAY(&mocks[2],(_UU32*)Test_statMock.callbackB.mock_p, 1);
  TEST_ASSERT_NULL(Test_statMock.callbackA.dataToSpy_p);
  TEST_ASSERT_NULL(Test_statMock.callbackB.dataToSpy_p);
}

static void Test_TestPopMockWithSpying(void)
{
  const _UU32 mocks[] = {0xFEED1011, 0xFEED2022, 0xFEED3033};
  const _UU8 dataA[] = {0xAA};
  const _UU8 dataB[] = {0xB0, 0xB1, 0xB2, 0xB3};
  const _UU8 dataC[] = {0xC0, 0xC1, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8};
  const _UU8 *datas[] = {dataA, dataB, dataC};
  const _UU32 sizes[] = {sizeof(dataA), sizeof(dataB), sizeof(dataC)};
  const _UU32 mockCount = STAT_ARRAY_LEN(mocks);
  const _UU32 allMocksSize = (sizeof(_StatMockBasicEntry_t) + sizeof(*mocks)) * mockCount;
  _UU32 allSpiesSize = 0;
  _UU32 index;

  for (index = 0; index < mockCount; index++)
  {
    STAT_ADD_MOCK(Test_TestPopMockWithSpying, mocks[index]);
    allSpiesSize += STAT_CEILING_ROUND(sizes[index], STAT_MOCK_MAX_ALIGNMENT);
  }

  TEST_ASSERT_EQUAL_HEX(mocks[0], *(_UU32*)STAT_POP_MOCK_WITH_SPYING(Test_TestPopMockWithSpying, dataA));
  TEST_ASSERT_EQUAL_HEX(mocks[1], *(_UU32*)STAT_POP_MOCK_WITH_SPYING(Test_TestPopMockWithSpying, dataB));
  TEST_ASSERT_EQUAL_HEX(mocks[2], *(_UU32*)STAT_POP_MOCK_WITH_SPYING(Test_TestPopMockWithSpying, dataC));
  TEST_ASSERT_EQUAL(mockCount, STAT_COUNT_CALLS(Test_TestPopMockWithSpying));

  TEST_ASSERT_EQUAL(STAT_MOCK_ALIGNED_SIZE - (allMocksSize + allSpiesSize),  Stat_GetMockFreeSpace());
  for (index = 0; index < mockCount; index++)
  {
    TEST_ASSERT_EQUAL_MEMORY(datas[index], STAT_GET_MOCK_SPY_DATA(Test_TestPopMockWithSpying, index), sizes[index]);
  }
}

static void Test_TestPopMocksWithSpyingAndCallbacks(void)
{
  const _UU32 mocks[] = {0xFEED1011, 0xFEED2022, 0xFEED3033};
  const STAT_MOCK_CALLBACK_T callbacks[] = 
    {Test_HandleMockCallbackA, Test_HandleMockCallbackA, Test_HandleMockCallbackB};
  const _UU32 spyData[] = {0xCEEDA1A1, 0xCEEDA2A2, 0xCEEDB3B3};
  const _UU32 mockCount = STAT_ARRAY_LEN(mocks);
  const _UU32 allMocksSize = (sizeof(_StatMockBasicEntry_t) + sizeof(*mocks) + sizeof(*callbacks)) * mockCount;
  const _UU32 allSpiesSize = sizeof(*spyData) * mockCount;
  _UU32 *received_p;
  _UU32 index;

  for (index = 0; index < mockCount; index++)
  {
    STAT_ADD_MOCK_WITH_CALLBACK(Test_TestMocksWithCallbacks, mocks[index], callbacks[index]);
  }

  for (index = 0; index < mockCount; index++)
  {
    TEST_ASSERT_EQUAL(index, STAT_COUNT_CALLS(Test_TestMocksWithCallbacks));
    received_p = STAT_POP_MOCK_WITH_SPYING_NUMERIC(Test_TestMocksWithCallbacks, spyData[index]);
    TEST_ASSERT_EQUAL_HEX(mocks[index], *received_p);
  }

  TEST_ASSERT_EQUAL(mockCount, STAT_COUNT_CALLS(Test_TestMocksWithCallbacks));
  TEST_ASSERT_EQUAL(STAT_MOCK_ALIGNED_SIZE - (allMocksSize + allSpiesSize),  Stat_GetMockFreeSpace());  
  TEST_ASSERT_EQUAL(2, Test_statMock.callbackA.callCount);
  TEST_ASSERT_EQUAL(1, Test_statMock.callbackB.callCount);
  TEST_ASSERT_EQUAL(2, Test_statMock.callbackA.callOrder);
  TEST_ASSERT_EQUAL(3, Test_statMock.callbackB.callOrder);
  TEST_ASSERT_EQUAL_HEX_ARRAY(&mocks[1],(_UU32*)Test_statMock.callbackA.mock_p, 1);
  TEST_ASSERT_EQUAL_HEX_ARRAY(&mocks[2],(_UU32*)Test_statMock.callbackB.mock_p, 1);
  TEST_ASSERT_EQUAL_HEX_ARRAY(&spyData[1],(_UU32*)Test_statMock.callbackA.dataToSpy_p, 1);
  TEST_ASSERT_EQUAL_HEX_ARRAY(&spyData[2],(_UU32*)Test_statMock.callbackB.dataToSpy_p, 1);
}

static void Test_TestAddEmptyMock(void)
{
  const _UU32 allMocksSize = (sizeof(_StatMockBasicEntry_t) * 3) + (sizeof(_UU32) * 2);
  
  STAT_ADD_NUMERIC_MOCK(Test_TestAddMock, 0x00000000UL);
  STAT_ADD_EMPTY_MOCK(Test_TestAddEmptyMock);
  STAT_ADD_NUMERIC_MOCK(Test_TestAddMock, 0xFFFFFFFFUL);

  TEST_ASSERT_EQUAL(STAT_MOCK_ALIGNED_SIZE - allMocksSize,  Stat_GetMockFreeSpace());
  TEST_ASSERT_EQUAL(0, Stat_CountAllCalls());

  TEST_ASSERT_NOT_NULL(_STAT_GET_MOCK_HANDLE(Test_TestAddEmptyMock, 0));
  TEST_ASSERT_EQUAL(0, STAT_GET_CALL_ORDER(Test_TestAddEmptyMock, 0));
  TEST_ASSERT_NULL(STAT_GET_MOCK_DATA(Test_TestAddEmptyMock, 0));
  TEST_ASSERT_NULL(STAT_GET_MOCK_SPY_DATA(Test_TestAddEmptyMock, 0));
  TEST_ASSERT_NULL(STAT_POP_MOCK(Test_TestAddEmptyMock));
  TEST_ASSERT_NULL(STAT_GET_MOCK_SPY_DATA(Test_TestAddEmptyMock, 0));
  TEST_ASSERT_EQUAL(1, STAT_GET_CALL_ORDER(Test_TestAddEmptyMock, 0));
}

static void Test_TestAddCallbackMock(void)
{
  const _UU32 allMocksSize = (sizeof(_StatMockBasicEntry_t) * 3) + (sizeof(_UU32) * 2) + sizeof(STAT_MOCK_CALLBACK_T);
  
  STAT_ADD_NUMERIC_MOCK(Test_TestAddMock, 0xAAAAAAAAUL);
  STAT_ADD_NUMERIC_MOCK(Test_TestAddMock, 0xBBBBBBBBUL);
  STAT_ADD_CALLBACK_MOCK(Test_TestAddCallbackMock, Test_HandleMockCallbackA);

  TEST_ASSERT_EQUAL(STAT_MOCK_ALIGNED_SIZE - allMocksSize,  Stat_GetMockFreeSpace());
  TEST_ASSERT_EQUAL(0, Stat_CountAllCalls());

  TEST_ASSERT_NOT_NULL(_STAT_GET_MOCK_HANDLE(Test_TestAddCallbackMock, 0));
  TEST_ASSERT_EQUAL(0, STAT_GET_CALL_ORDER(Test_TestAddCallbackMock, 0));
  TEST_ASSERT_NULL(STAT_GET_MOCK_DATA(Test_TestAddCallbackMock, 0));
  TEST_ASSERT_NULL(STAT_GET_MOCK_SPY_DATA(Test_TestAddCallbackMock, 0));
  TEST_ASSERT_NULL(STAT_POP_MOCK(Test_TestAddCallbackMock));
  TEST_ASSERT_NULL(STAT_GET_MOCK_SPY_DATA(Test_TestAddCallbackMock, 0));
  TEST_ASSERT_EQUAL(1, STAT_GET_CALL_ORDER(Test_TestAddCallbackMock, 0));

  TEST_ASSERT_EQUAL(1, Test_statMock.callbackA.callCount);
  TEST_ASSERT_EQUAL(1, Test_statMock.callbackA.callOrder);
  TEST_ASSERT_NULL(Test_statMock.callbackA.mock_p);
  TEST_ASSERT_NULL(Test_statMock.callbackA.dataToSpy_p);
}

static void Test_TestAddManyMocks(void)
{
  _UU32 next;
  const _TestMockOject_t mocks[] = {{0x10001000, 0x10002000}, {0xDEADBEEF, 0xFACEACAD}, {0x33333331, 0x33333332}};
  const _UU32 allMocksSize = (sizeof(_StatMockBasicEntry_t) + sizeof(*mocks)) * STAT_ARRAY_LEN(mocks);

  STAT_ADD_MANY_MOCKS(Test_TestAddManyMocks, mocks, STAT_ARRAY_LEN(mocks));

  TEST_ASSERT_EQUAL(STAT_MOCK_ALIGNED_SIZE - allMocksSize,  Stat_GetMockFreeSpace());

  for (next = 0; next < STAT_ARRAY_LEN(mocks); next++)
  {
    TEST_ASSERT_EQUAL_MEMORY(&mocks[next], STAT_POP_MOCK(Test_TestAddManyMocks), sizeof(_TestMockOject_t));
  }  
}

static void Test_TestSpyingAfterAddMultipleMocks(void)
{
  _UU32 next;
  _UU32 simpleMocks[] = {0xFACEADAD, 0xFEEDACAD};
  _UU16 smallMocks[] = {0x1000, 0x2000, 0x3000, 0x4000};
  _UU8 spyData[] = {0xAA, 0x55, 0xBB, 0x01, 0xCC, 0x37, 0xDD};

  STAT_ADD_MANY_MOCKS(Test_TestSpyingAfterAddMultipleMocks, simpleMocks, STAT_ARRAY_LEN(simpleMocks));
  STAT_ADD_MANY_MOCKS(Test_TestAddManyMocks, smallMocks, STAT_ARRAY_LEN(smallMocks));

  for (next = 0; next < STAT_ARRAY_LEN(simpleMocks); next++)
  {
    TEST_ASSERT_EQUAL_HEX(simpleMocks[next], 
      *(_UU32*)STAT_POP_MOCK_WITH_SPYING_NUMERIC(Test_TestSpyingAfterAddMultipleMocks, 7 * next));
    TEST_ASSERT_EQUAL_HEX(smallMocks[next], *(_UU16*)STAT_POP_MOCK_WITH_SPYING(Test_TestAddManyMocks, spyData));
  }

  for (; next < STAT_ARRAY_LEN(smallMocks); next++)
  {
    TEST_ASSERT_EQUAL_HEX(smallMocks[next], *(_UU16*)STAT_POP_MOCK_WITH_SPYING(Test_TestAddManyMocks, spyData));
  }

  for (next = 0; next < STAT_ARRAY_LEN(simpleMocks); next++)
  {
    TEST_ASSERT_EQUAL_HEX(7 * next, *(_UU32*)STAT_GET_MOCK_SPY_DATA(Test_TestSpyingAfterAddMultipleMocks, next));
  }
  
  for (next = 0; next < STAT_ARRAY_LEN(smallMocks); next++)
  {
    TEST_ASSERT_EQUAL_HEX8_ARRAY(spyData, STAT_GET_MOCK_SPY_DATA(Test_TestAddManyMocks, next), sizeof(spyData));
  }
}

static void Test_TestCallbackUponAddMultipleMocks(void)
{
  _TestMockOject_t mocks[] = {{0x10001000, 0x10002000}, {0xDEADBEEF, 0xFACEACAD}};
  _UU8 spyData[] = {0xAA, 0x55, 0xBB, 0x01, 0xCC, 0x37, 0xDD};
  
  STAT_ADD_MANY_MOCKS_WITH_CALLBACK(Test_TestCallbackUponAddMultipleMocks, mocks, STAT_ARRAY_LEN(mocks), 
    Test_HandleMockCallbackA);

  STAT_POP_MOCK(Test_TestCallbackUponAddMultipleMocks);
  TEST_ASSERT_EQUAL(1, Test_statMock.callbackA.callCount);
  TEST_ASSERT_EQUAL(1, Test_statMock.callbackA.callOrder);
  TEST_ASSERT_EQUAL_MEMORY_ARRAY(&mocks[0],(_TestMockOject_t*)Test_statMock.callbackA.mock_p, 
    sizeof(_TestMockOject_t), 1);
  TEST_ASSERT_NULL(Test_statMock.callbackA.dataToSpy_p);
  
  STAT_POP_MOCK_WITH_SPYING(Test_TestCallbackUponAddMultipleMocks, spyData);
  TEST_ASSERT_EQUAL(2, Test_statMock.callbackA.callCount);
  TEST_ASSERT_EQUAL(2, Test_statMock.callbackA.callOrder);
  TEST_ASSERT_EQUAL_MEMORY_ARRAY(&mocks[1],(_TestMockOject_t*)Test_statMock.callbackA.mock_p, 
    sizeof(_TestMockOject_t), 1);
  TEST_ASSERT_EQUAL_HEX8_ARRAY(spyData, Test_statMock.callbackA.dataToSpy_p, sizeof(spyData));
}

static void Test_TestGetMockHandle(void)
{
  _UU32 index;
  _StatMockBasicEntry_t *actual_p;
  const _UU32 firstSetMocksCount = 2;
  const _UU32 secondSetMocksCount = 3;

  for (index = 0; index < firstSetMocksCount; index++)
  {
    STAT_ADD_NUMERIC_MOCK(Test_TestAddMock, index);
  }
  for (index = 0; index < secondSetMocksCount; index++)
  {
    STAT_ADD_NUMERIC_MOCK(Test_TestGetMockHandle, index);
  }

  for (index = 0; index < firstSetMocksCount; index++)
  {
    actual_p = _STAT_GET_MOCK_HANDLE(Test_TestAddMock, index);
    TEST_ASSERT_EQUAL_STRING("Test_TestAddMock", actual_p->declarator_p);
    TEST_ASSERT_EQUAL_HEX(index, *(_UU32*)(actual_p + 1));
  }
  for (index = 0; index < secondSetMocksCount; index++)
  {
    actual_p = _STAT_GET_MOCK_HANDLE(Test_TestGetMockHandle, index);
    TEST_ASSERT_EQUAL_STRING("Test_TestGetMockHandle", actual_p->declarator_p);
    TEST_ASSERT_EQUAL_HEX(index, *(_UU32*)(actual_p + 1));
  }
  
  TEST_ASSERT_NULL(_STAT_GET_MOCK_HANDLE(Test_TestAddMock, firstSetMocksCount));
  TEST_ASSERT_NULL(_STAT_GET_MOCK_HANDLE(Test_TestGetMockHandle, secondSetMocksCount));
  TEST_ASSERT_NULL(_STAT_GET_MOCK_HANDLE(Test_TestAddEmptyMock, 0));
}

static void Test_TestSpyOn(void)
{
  const _UU8 data[] = {0xD1, 0xD1, 0xD1, 0xD1, 0xD1, 0xD1, 0xD1, 0xD1,  0xD1};
  const _UU32 dataSize = STAT_ARRAY_LEN(data);
  const _UU32 allocatedSize = sizeof(_StatMockBasicEntry_t) + STAT_CEILING_ROUND(dataSize, STAT_MOCK_MAX_ALIGNMENT);

  STAT_SPY_ON_WITHOUT_MOCK(Test_TestSpyOn, data);

  TEST_ASSERT_EQUAL(STAT_MOCK_ALIGNED_SIZE - allocatedSize,  Stat_GetMockFreeSpace());
  TEST_ASSERT_EQUAL(1, Stat_CountAllCalls());
  TEST_ASSERT_EQUAL(1, STAT_COUNT_CALLS(Test_TestSpyOn));

  TEST_ASSERT_NOT_NULL(_STAT_GET_MOCK_HANDLE(Test_TestSpyOn, 0));
  TEST_ASSERT_EQUAL(1, STAT_GET_CALL_ORDER(Test_TestSpyOn, 0));
  TEST_ASSERT_EQUAL_UINT8_ARRAY(data, STAT_GET_MOCK_SPY_DATA(Test_TestSpyOn, 0), dataSize);
}

static void Test_TestMultipleSpyOn(void)
{
  _UU32 index;
  const _UU32 data[] = {0xA1A1A1A1UL, 0xAAAA2222UL, 0x1BB1B11BUL, 0xBB2222BBUL, 0xBB33BB33UL, 0xFEFEFEFEUL};
  const _UU32 count = STAT_ARRAY_LEN(data);
  const _UU32 allocatedSize = sizeof(_StatMockBasicEntry_t) + (sizeof(_StatMockBasicEntry_t) + sizeof(*data)) * count;

  STAT_ADD_EMPTY_MOCK(Test_TestAddEmptyMock);
  
  for (index = 0; index < count;)
  {
    STAT_SPY_ON_WITHOUT_MOCK(Test_TestMultipleSpyOn, data[index++]);
    STAT_SPY_ON_NUMERIC_WITHOUT_MOCK(Test_TestMultipleSpyOn, data[index++]);
  }

  TEST_ASSERT_EQUAL(STAT_MOCK_ALIGNED_SIZE - allocatedSize,  Stat_GetMockFreeSpace());
  TEST_ASSERT_EQUAL(count, Stat_CountAllCalls());
  TEST_ASSERT_EQUAL(count, STAT_COUNT_CALLS(Test_TestMultipleSpyOn));

  for (index = 0; index < count; index++)
  {
    TEST_ASSERT_NOT_NULL(_STAT_GET_MOCK_HANDLE(Test_TestMultipleSpyOn, index));
    TEST_ASSERT_EQUAL(1 + index, STAT_GET_CALL_ORDER(Test_TestMultipleSpyOn, index));
    TEST_ASSERT_EQUAL_HEX(data[index], *(_UU32*)STAT_GET_MOCK_SPY_DATA(Test_TestMultipleSpyOn, index));    
  }
}

static void Test_TestCountCallables(void)
{
  TEST_ASSERT_EQUAL(0, STAT_COUNT_TEST_CALLABLES(Test_TestCountCallables));

  STAT_ADD_NUMERIC_MOCK(Test_TestAddMock, Stat_Rand());
  STAT_SPY_ON_NUMERIC_WITHOUT_MOCK(Test_TestSpyOn, Stat_Rand());
  TEST_ASSERT_EQUAL(0, STAT_COUNT_TEST_CALLABLES(Test_TestCountCallables));

  STAT_SPY_ON_NUMERIC_WITHOUT_MOCK(Test_TestCountCallables, Stat_Rand());
  TEST_ASSERT_EQUAL(1, STAT_COUNT_TEST_CALLABLES(Test_TestCountCallables));

  STAT_ADD_NUMERIC_MOCK(Test_TestCountCallables, Stat_Rand());
  STAT_POP_MOCK(Test_TestCountCallables);
  TEST_ASSERT_EQUAL(2, STAT_COUNT_TEST_CALLABLES(Test_TestCountCallables));

  STAT_ADD_NUMERIC_MOCK(Test_TestCountCallables, Stat_Rand());
  STAT_ADD_EMPTY_MOCK(Test_TestCountCallables);
  STAT_ADD_CALLBACK_MOCK(Test_TestCountCallables, Test_HandleMockCallbackA);
  TEST_ASSERT_EQUAL(5, STAT_COUNT_TEST_CALLABLES(Test_TestCountCallables));
}

static void Test_TestCountCalls(void)
{
  TEST_ASSERT_EQUAL(0, STAT_COUNT_CALLS(Test_TestCountCalls));
  STAT_SPY_ON_NUMERIC_WITHOUT_MOCK(Test_TestCountCalls, (_UU32)(-1));
  TEST_ASSERT_EQUAL(1, STAT_COUNT_CALLS(Test_TestCountCalls));
  STAT_SPY_ON_NUMERIC_WITHOUT_MOCK(Test_TestCountCalls, 0);
  TEST_ASSERT_EQUAL(2, STAT_COUNT_CALLS(Test_TestCountCalls));
}

static void Test_TestHasMocks(void)
{
  TEST_ASSERT_FALSE(STAT_HAS_MOCKS(Test_TestHasMocks));

  STAT_SPY_ON_NUMERIC_WITHOUT_MOCK(Test_TestHasMocks, Stat_Rand());
  TEST_ASSERT_FALSE(STAT_HAS_MOCKS(Test_TestHasMocks));

  STAT_ADD_NUMERIC_MOCK(Test_TestAddMock, Stat_Rand());
  TEST_ASSERT_FALSE(STAT_HAS_MOCKS(Test_TestHasMocks));

  STAT_ADD_NUMERIC_MOCK(Test_TestHasMocks, Stat_Rand());
  TEST_ASSERT_TRUE(STAT_HAS_MOCKS(Test_TestHasMocks));

  STAT_POP_MOCK(Test_TestHasMocks);
  TEST_ASSERT_TRUE(STAT_HAS_MOCKS(Test_TestHasMocks));
}

static void Test_TestHasUnconsumedMocks(void)
{
  TEST_ASSERT_FALSE(STAT_HAS_UNCONSUMED_MOCKS(Test_TestHasUnconsumedMocks));

  STAT_SPY_ON_NUMERIC_WITHOUT_MOCK(Test_TestHasUnconsumedMocks, Stat_Rand());
  TEST_ASSERT_FALSE(STAT_HAS_UNCONSUMED_MOCKS(Test_TestHasUnconsumedMocks));

  STAT_ADD_NUMERIC_MOCK(Test_TestAddMock, Stat_Rand());
  TEST_ASSERT_FALSE(STAT_HAS_UNCONSUMED_MOCKS(Test_TestHasUnconsumedMocks));

  STAT_ADD_NUMERIC_MOCK(Test_TestHasUnconsumedMocks, Stat_Rand());
  TEST_ASSERT_TRUE(STAT_HAS_UNCONSUMED_MOCKS(Test_TestHasUnconsumedMocks));

  STAT_POP_MOCK(Test_TestHasUnconsumedMocks);
  TEST_ASSERT_FALSE(STAT_HAS_UNCONSUMED_MOCKS(Test_TestHasUnconsumedMocks));

  STAT_ADD_NUMERIC_MOCK(Test_TestHasUnconsumedMocks, Stat_Rand());
  TEST_ASSERT_TRUE(STAT_HAS_UNCONSUMED_MOCKS(Test_TestHasUnconsumedMocks));
}

static void Test_TestFindUnconsumedMock(void)
{
  _StatMockBasicEntry_t *entry_p;
  
  TEST_ASSERT_NULL(Stat_FindAnyUnconsumedMockEntry());
  
  STAT_ADD_NUMERIC_MOCK(Test_TestAddMock, Stat_Rand());
  STAT_ADD_NUMERIC_MOCK(Test_TestAddEmptyMock, Stat_Rand());
  STAT_ADD_NUMERIC_MOCK(Test_TestFindUnconsumedMock, Stat_Rand());
  STAT_ADD_NUMERIC_MOCK(Test_TestFindUnconsumedMock, Stat_Rand());
  STAT_ADD_NUMERIC_MOCK(Test_TestAddEmptyMock, Stat_Rand());

  entry_p = _STAT_GET_MOCK_HANDLE(Test_TestAddMock, 0);
  TEST_ASSERT_EQUAL_PTR(entry_p, Stat_FindAnyUnconsumedMockEntry());

  STAT_POP_MOCK(Test_TestAddEmptyMock);
  TEST_ASSERT_EQUAL_PTR(entry_p, Stat_FindAnyUnconsumedMockEntry());

  STAT_POP_MOCK(Test_TestAddEmptyMock);
  TEST_ASSERT_EQUAL_PTR(entry_p, Stat_FindAnyUnconsumedMockEntry());

  STAT_POP_MOCK(Test_TestAddMock);
  entry_p = _STAT_GET_MOCK_HANDLE(Test_TestFindUnconsumedMock, 0);
  TEST_ASSERT_EQUAL_PTR(entry_p, Stat_FindAnyUnconsumedMockEntry());

  STAT_POP_MOCK(Test_TestFindUnconsumedMock);
  entry_p = _STAT_GET_MOCK_HANDLE(Test_TestFindUnconsumedMock, 1);
  TEST_ASSERT_EQUAL_PTR(entry_p, Stat_FindAnyUnconsumedMockEntry());

  STAT_POP_MOCK(Test_TestFindUnconsumedMock);
  TEST_ASSERT_NULL(Stat_FindAnyUnconsumedMockEntry());
}

static void Test_TestMockTeardown(void)
{
  Stat_TearDownMock();
  
  Stat_SetupMock();
  STAT_ADD_NUMERIC_MOCK(Test_TestMockTeardown, Stat_Rand());
  STAT_POP_MOCK(Test_TestMockTeardown);
  Stat_TearDownMock();

  Stat_SetupMock();
  STAT_ADD_NUMERIC_MOCK(Test_TestMockTeardown, Stat_Rand());
  STAT_ADD_NUMERIC_MOCK(Test_TestMockTeardown, Stat_Rand());
  STAT_POP_MOCK(Test_TestMockTeardown);
  TEST_ABORT_UPON_NON_STAT_MOCK_PERMISSIVE_VALIDATION();
  Stat_TearDownMock();
  
  TEST_FAIL_MESSAGE("The test should not reach this point due to expected test-abort!");
}

static void Test_TestAddMockNoOverflow(void)
{
  const _UU8 mock[STAT_MOCK_ALIGNED_SIZE - sizeof(_StatMockBasicEntry_t)] = {0};
  STAT_ADD_MOCK(Test_TestAddMockNoOverflow, mock);
}

static void Test_TestAddMockWithOverflow(void)
{
  const _UU8 mock[STAT_MOCK_ALIGNED_SIZE - sizeof(_StatMockBasicEntry_t)] = {0};
  
  STAT_ADD_EMPTY_MOCK(Test_TestAddMockWithOverflow);
  
  TEST_ABORT_UPON_NON_STAT_MOCK_PERMISSIVE_VALIDATION();
  STAT_ADD_MOCK(Test_TestAddMockWithOverflow, mock);
  TEST_FAIL_MESSAGE("The test should not reach this point due to expected test-abort!");
}

static void Test_TestPopMockWithSpyNoOverflow(void)
{
  const _UU8 data[STAT_MOCK_ALIGNED_SIZE - sizeof(_StatMockBasicEntry_t)] = {-1};

  STAT_ADD_EMPTY_MOCK(Test_TestPopMockWithSpyNoOverflow);
  STAT_POP_MOCK_WITH_SPYING(Test_TestPopMockWithSpyNoOverflow, data);
  TEST_ASSERT_EQUAL_HEX8_ARRAY(data, STAT_GET_MOCK_SPY_DATA(Test_TestPopMockWithSpyNoOverflow, 0), sizeof(data));
}

static void Test_TestPopMockWithSpyWithOverflow(void)
{
  const _UU8 data[STAT_MOCK_ALIGNED_SIZE - sizeof(_StatMockBasicEntry_t)] = {-1};

  STAT_ADD_EMPTY_MOCK(Test_TestPopMockWithSpyWithOverflow);
  STAT_ADD_EMPTY_MOCK(Test_TestPopMockWithSpyWithOverflow);

  TEST_ABORT_UPON_NON_STAT_MOCK_PERMISSIVE_VALIDATION();
  STAT_POP_MOCK_WITH_SPYING(Test_TestPopMockWithSpyWithOverflow, data);
  TEST_FAIL_MESSAGE("The test should not reach this point due to expected test-abort!");
}

static void Test_TestSpyOnWithoutOverflow(void)
{
  const _UU8 data[STAT_MOCK_ALIGNED_SIZE - sizeof(_StatMockBasicEntry_t)] = {1, 2, 3, 4, 5, 6, 7};
  STAT_SPY_ON_WITHOUT_MOCK(Test_TestSpyOnWithoutOverflow, data);
  TEST_ASSERT_EQUAL_HEX8_ARRAY(data, STAT_GET_MOCK_SPY_DATA(Test_TestSpyOnWithoutOverflow, 0), sizeof(data));
}

static void Test_TestSpyOnWithOverflow(void)
{
  const _UU8 data[STAT_MOCK_ALIGNED_SIZE - sizeof(_StatMockBasicEntry_t)] = {1, 2, 3, 4, 5, 6, 7};

  STAT_ADD_EMPTY_MOCK(Test_TestSpyOnWithoutOverflow);

  TEST_ABORT_UPON_NON_STAT_MOCK_PERMISSIVE_VALIDATION();
  STAT_SPY_ON_WITHOUT_MOCK(Test_TestSpyOnWithOverflow, data);
  TEST_FAIL_MESSAGE("The test should not reach this point due to expected test-abort!");
}

static void Test_TestGetSpyDataOutOfBound(void)
{
  _UU32 index;
  const _UU32 mocks[] = {0xFEED1011, 0xFEED2022, 0xFEED3033};

  for (index = 0; index < STAT_ARRAY_LEN(mocks); index++)
  {
    STAT_SPY_ON_NUMERIC_WITHOUT_MOCK(Test_TestGetSpyDataOutOfBound, mocks[index]);
  }
  for (index = 0; index < STAT_ARRAY_LEN(mocks); index++)
  {
    TEST_ASSERT_EQUAL_HEX(mocks[index], *(_UU32*)STAT_GET_MOCK_SPY_DATA(Test_TestGetSpyDataOutOfBound, index));
  }
  TEST_ABORT_UPON_NON_STAT_MOCK_PERMISSIVE_VALIDATION();

  STAT_GET_MOCK_SPY_DATA(Test_TestGetSpyDataOutOfBound, index);
  TEST_FAIL_MESSAGE("The test should not reach this point due to expected test-abort!");
}

static void Test_TestGetCallOrderDataOutOfBound(void)
{
  _UU32 index;
  const _UU32 mocks[] = {0xFEED1011, 0xFEED2022, 0xFEED3033};

  for (index = 0; index < STAT_ARRAY_LEN(mocks); index++)
  {
    STAT_SPY_ON_NUMERIC_WITHOUT_MOCK(Test_TestGetCallOrderDataOutOfBound, mocks[index]);
  }
  for (index = 0; index < STAT_ARRAY_LEN(mocks); index++)
  {
    TEST_ASSERT_EQUAL(index + 1, STAT_GET_CALL_ORDER(Test_TestGetCallOrderDataOutOfBound, index));
  }
  TEST_ABORT_UPON_NON_STAT_MOCK_PERMISSIVE_VALIDATION();

  STAT_GET_CALL_ORDER(Test_TestGetCallOrderDataOutOfBound, index);
  TEST_FAIL_MESSAGE("The test should not reach this point due to expected test-abort!");
}

static void Test_TestCallOrderBeyondNaturalLimitForSpys(void)
{
#if (STAT_MOCK_METADATA_CALL_ORDER < STAT_MOCK_CALL_EXTENDED_CALL_ORDER)
  _UU32 index;
  _UU32 spyData;
  _UU32 mockBase = 0xFACE0000UL;

  for (index = 0; index < (STAT_MOCK_CALL_ORDER_NATURAL_MAX + 2); index++)
  {
    spyData = mockBase + index;
    STAT_SPY_ON_WITHOUT_MOCK(Test_TestCallOrderBeyondNaturalLimitForSpys, spyData);
    
    TEST_ASSERT_EQUAL(index + 1, STAT_GET_CALL_ORDER(Test_TestCallOrderBeyondNaturalLimitForSpys, index));
    TEST_ASSERT_EQUAL(spyData, *(_UU32*)STAT_GET_MOCK_SPY_DATA(Test_TestCallOrderBeyondNaturalLimitForSpys, index));
  }
#else
  TEST_IGNORE_MESSAGE("The test is not relevant for jumbo configurations of STAT-Mock!")
#endif
}

static void Test_TestCallOrderBeyondNaturalLimitForMocks(void)
{
#if (STAT_MOCK_METADATA_CALL_ORDER < STAT_MOCK_CALL_EXTENDED_CALL_ORDER)
  _UU32 index;
  _UU32 spyData;
  _UU32 mockBase = 0xFADE0000UL;

  for (index = 0; index < (STAT_MOCK_CALL_ORDER_NATURAL_MAX + 2); index++)
  {
    spyData = mockBase + index;
    STAT_ADD_CALLBACK_MOCK(Test_TestCallOrderBeyondNaturalLimitForMocks, Test_HandleMockCallbackA);
    STAT_POP_MOCK_WITH_SPYING(Test_TestCallOrderBeyondNaturalLimitForMocks, spyData);
    
    TEST_ASSERT_EQUAL(index + 1, STAT_GET_CALL_ORDER(Test_TestCallOrderBeyondNaturalLimitForMocks, index));
    TEST_ASSERT_EQUAL(Test_statMock.callbackA.callCount, Test_statMock.callbackA.callOrder);
    TEST_ASSERT_EQUAL(spyData, *(_UU32*)STAT_GET_MOCK_SPY_DATA(Test_TestCallOrderBeyondNaturalLimitForMocks, index));
    TEST_ASSERT_EQUAL(spyData, *(_UU32*)Test_statMock.callbackA.dataToSpy_p);
  }

  STAT_ADD_CALLBACK_MOCK(Test_TestCallOrderBeyondNaturalLimitForMocks, Test_HandleMockCallbackA);
  STAT_POP_MOCK(Test_TestCallOrderBeyondNaturalLimitForMocks);
  TEST_ASSERT_NULL(STAT_GET_MOCK_SPY_DATA(Test_TestCallOrderBeyondNaturalLimitForMocks, index));
  TEST_ASSERT_NULL(Test_statMock.callbackA.dataToSpy_p);
#else
  TEST_IGNORE_MESSAGE("The test is not relevant for jumbo configurations of STAT-Mock!")
#endif
}

static void Test_TestCallOrderTrackingUponNoViolation(void)
{
  STAT_ADD_CALLBACK_MOCK(Test_TestCallOrderTrackingUponNoViolation, Test_EnforceCallOrderTracking);
  STAT_ADD_EMPTY_MOCK(Test_TestMockInitialization);
  STAT_ADD_EMPTY_MOCK(Test_TestAddEmptyMock);
  STAT_ADD_EMPTY_MOCK(Test_TestAddManyMocks);
  STAT_ADD_EMPTY_MOCK(Test_TestCallOrderTrackingUponOrderViolation);
  STAT_ADD_CALLBACK_MOCK(Test_TestAddCallbackMock, Test_CeaseCallOrderTracking);

  STAT_ADD_EMPTY_MOCK(Test_TestAddMock);
  STAT_ADD_EMPTY_MOCK(Test_TestSpyOn);

  STAT_POP_MOCK(Test_TestSpyOn);

  STAT_POP_MOCK(Test_TestCallOrderTrackingUponNoViolation);
  STAT_POP_MOCK(Test_TestMockInitialization);
  STAT_POP_MOCK(Test_TestAddEmptyMock);
  STAT_POP_MOCK(Test_TestAddManyMocks);
  STAT_POP_MOCK(Test_TestCallOrderTrackingUponOrderViolation);
  STAT_POP_MOCK(Test_TestAddCallbackMock);

  STAT_POP_MOCK(Test_TestAddMock);
}

static void Test_TestCallOrderTrackingUponOrderViolation(void)
{
  STAT_ADD_CALLBACK_MOCK(Test_TestCallOrderTrackingUponNoViolation, Test_EnforceCallOrderTracking);
  STAT_ADD_EMPTY_MOCK(Test_TestMockInitialization);
  STAT_ADD_EMPTY_MOCK(Test_TestAddEmptyMock);
  STAT_ADD_EMPTY_MOCK(Test_TestAddManyMocks);
  STAT_ADD_EMPTY_MOCK(Test_TestCallOrderTrackingUponOrderViolation);
  STAT_ADD_CALLBACK_MOCK(Test_TestAddCallbackMock, Test_CeaseCallOrderTracking);

  STAT_ADD_EMPTY_MOCK(Test_TestAddMock);
  STAT_ADD_EMPTY_MOCK(Test_TestSpyOn);
  
  STAT_POP_MOCK(Test_TestSpyOn);

  STAT_POP_MOCK(Test_TestCallOrderTrackingUponNoViolation);
  STAT_POP_MOCK(Test_TestMockInitialization);
  STAT_POP_MOCK(Test_TestAddEmptyMock);
  TEST_ABORT_UPON_NON_STAT_MOCK_PERMISSIVE_VALIDATION();
  STAT_POP_MOCK(Test_TestCallOrderTrackingUponOrderViolation);
  TEST_FAIL_MESSAGE("The test should not reach this point due to expected test-abort!");
}

static void Test_TestSingleCallToOverriddenMock(void)
{
  _UU32 spyData = Stat_Rand();
  void* received_p;
  const _UU32 allMocksSize = sizeof(_StatMockBasicEntry_t) + sizeof(STAT_MOCK_HANDLER_T);
  
  Test_statMock.overrideHandler.mock_p = (void*)Stat_Rand();
  
  STAT_OVERRIDE_MOCK(Test_TestSingleCallToOverriddenMock, Test_OverrideMock);
  TEST_ASSERT_EQUAL(1, STAT_COUNT_TEST_CALLABLES(Test_TestSingleCallToOverriddenMock));
  TEST_ASSERT_TRUE(STAT_HAS_MOCKS(Test_TestSingleCallToOverriddenMock));
  TEST_ASSERT_EQUAL(STAT_MOCK_ALIGNED_SIZE - allMocksSize,  Stat_GetMockFreeSpace());

  received_p = STAT_POP_MOCK_WITH_SPYING(Test_TestSingleCallToOverriddenMock, spyData);
  TEST_ASSERT_EQUAL_PTR(Test_statMock.overrideHandler.mock_p, received_p);
  TEST_ASSERT_EQUAL_HEX(spyData, *(_UU32*)Test_statMock.overrideHandler.dataToSpy_p);
  TEST_ASSERT_EQUAL(1, Test_statMock.overrideHandler.callOrder);
  TEST_ASSERT_EQUAL(1, Test_statMock.overrideHandler.callCount);
  TEST_ASSERT_EQUAL(1, STAT_COUNT_CALLS(Test_TestSingleCallToOverriddenMock));
  TEST_ASSERT_EQUAL(0, STAT_GET_CALL_ORDER(Test_TestSingleCallToOverriddenMock, 0));
  TEST_ASSERT_NULL(STAT_GET_MOCK_SPY_DATA(Test_TestSingleCallToOverriddenMock, 0));
  TEST_ASSERT_NULL(STAT_GET_MOCK_DATA(Test_TestSingleCallToOverriddenMock, 0));
  TEST_ASSERT_TRUE(STAT_HAS_UNCONSUMED_MOCKS(Test_TestSingleCallToOverriddenMock));

  Stat_TearDownMock();
}

static void Test_TestMultipleCallToOverriddenMock(void)
{
  _UU32 spyData = Stat_Rand();
  void* received_p;
  STAT_ADD_EMPTY_MOCK(Test_TestAddMock);
  STAT_ADD_EMPTY_MOCK(Test_TestAddMock);

  STAT_OVERRIDE_MOCK(Test_TestMultipleCallToOverriddenMock, Test_OverrideMock);
  
  STAT_ADD_EMPTY_MOCK(Test_TestAddEmptyMock);
  STAT_ADD_EMPTY_MOCK(Test_TestAddManyMocks);

  STAT_POP_MOCK(Test_TestAddMock);
  STAT_POP_MOCK(Test_TestMultipleCallToOverriddenMock);
  STAT_POP_MOCK(Test_TestAddEmptyMock);
  STAT_POP_MOCK(Test_TestMultipleCallToOverriddenMock);
  TEST_ASSERT_NULL(Test_statMock.overrideHandler.dataToSpy_p);
  
  received_p = STAT_POP_MOCK_WITH_SPYING(Test_TestMultipleCallToOverriddenMock, spyData);
  TEST_ASSERT_EQUAL_PTR(Test_statMock.overrideHandler.mock_p, received_p);
  TEST_ASSERT_EQUAL_HEX(spyData, *(_UU32*)Test_statMock.overrideHandler.dataToSpy_p);
  TEST_ASSERT_EQUAL(5, Test_statMock.overrideHandler.callOrder);
  TEST_ASSERT_EQUAL(3, Test_statMock.overrideHandler.callCount);
  TEST_ASSERT_EQUAL(3, STAT_COUNT_CALLS(Test_TestMultipleCallToOverriddenMock));
  TEST_ASSERT_EQUAL(5, Stat_CountAllCalls());
}

// TODO: ???Check that overridden mock doesn't distort the call order enforcing?????

static void Test_TestAddReusableMockForSingleUse(void)
{
  _UU32 spyData = Stat_Rand();
  
  STAT_ADD_REUSABLE_NUMERIC_MOCK(Test_TestAddReusableMockForSingleUse, 0xFEEDACAD, 1);

  TEST_ASSERT_TRUE(STAT_HAS_MOCKS(Test_TestAddReusableMockForSingleUse));
  TEST_ASSERT_TRUE(STAT_HAS_UNCONSUMED_MOCKS(Test_TestAddReusableMockForSingleUse));
  TEST_ASSERT_EQUAL(0, STAT_COUNT_CALLS(Test_TestAddReusableMockForSingleUse));
  TEST_ASSERT_EQUAL(1, STAT_COUNT_TEST_CALLABLES(Test_TestAddReusableMockForSingleUse));

  TEST_ASSERT_EQUAL_HEX(0xFEEDACAD, *(_UU32*)STAT_POP_MOCK_WITH_SPYING(Test_TestAddReusableMockForSingleUse, spyData));

  TEST_ASSERT_FALSE(STAT_HAS_UNCONSUMED_MOCKS(Test_TestAddReusableMockForSingleUse));  
  TEST_ASSERT_EQUAL(1, STAT_COUNT_CALLS(Test_TestAddReusableMockForSingleUse));
  TEST_ASSERT_EQUAL_HEX(spyData, *(_UU32*)STAT_GET_MOCK_SPY_DATA(Test_TestAddReusableMockForSingleUse, 0));
}

static void Test_TestAddNumericReusableMock(void)
{
  _UU32 mock = Stat_Rand();
  _UU32 useCount = Stat_RandRange(20, 30);
  _UU32 spyData;
  _UU32 index;
  
  STAT_ADD_REUSABLE_NUMERIC_MOCK(Test_TestAddNumericReusableMock, mock, useCount);
  TEST_ASSERT_EQUAL(useCount, STAT_COUNT_TEST_CALLABLES(Test_TestAddNumericReusableMock));

  for (index = 0; index < useCount; index++)
  {
    spyData = index;
    TEST_ASSERT_EQUAL_HEX(mock, *(_UU32*)STAT_POP_MOCK_WITH_SPYING(Test_TestAddNumericReusableMock, spyData));
    TEST_ASSERT_EQUAL(index + 1, STAT_COUNT_CALLS(Test_TestAddNumericReusableMock));
    TEST_ASSERT_EQUAL_HEX(spyData, *(_UU32*)STAT_GET_MOCK_SPY_DATA(Test_TestAddNumericReusableMock, index));
  }
}

static void Test_TestSpiedDataUponReusableMock(void)
{
  _UU8 spyData[] = {0xFF, 0xFA, 0xCE, 0xAC, 0xAD, 0xFE, 0xED};
  _UU32 count = sizeof(spyData);
  _UU32 index;
  
  STAT_ADD_REUSABLE_NUMERIC_MOCK(Test_TestSpiedDataUponReusableMock, Stat_Rand(), count);
  STAT_ADD_REUSABLE_NUMERIC_MOCK(Test_TestAddNumericReusableMock, Stat_Rand(), count);

  for (index = 0; index < count; index++)
  {
    spyData[index] = count - 1;
    STAT_POP_MOCK_WITH_SPYING(Test_TestSpiedDataUponReusableMock, spyData);
    STAT_POP_MOCK(Test_TestAddNumericReusableMock);
  }

  for (index = 0; index < count; index++)
  {
    TEST_ASSERT_EQUAL_HEX8_ARRAY(spyData, 
      STAT_GET_MOCK_SPY_DATA(Test_TestSpiedDataUponReusableMock, index), count);
    TEST_ASSERT_NULL(STAT_GET_MOCK_SPY_DATA(Test_TestAddNumericReusableMock, index));
  }
}

static void Test_TestStatisticsUponReusableMock(void)
{
  _UU32 count = Stat_RandRange(20, 30);
  _UU32 index;
  _UU32 callOrder;
  _UU32 firstMock = Stat_Rand();
  _UU8 secondMock = (_UU8)Stat_Rand();
  
  STAT_ADD_REUSABLE_MOCK(Test_TestSpiedDataUponReusableMock, firstMock, count);
  STAT_ADD_REUSABLE_MOCK(Test_TestStatisticsUponReusableMock, secondMock, count);

  TEST_ASSERT_TRUE(STAT_HAS_MOCKS(Test_TestSpiedDataUponReusableMock));
  TEST_ASSERT_TRUE(STAT_HAS_MOCKS(Test_TestStatisticsUponReusableMock));
  TEST_ASSERT_TRUE(STAT_HAS_UNCONSUMED_MOCKS(Test_TestSpiedDataUponReusableMock));
  TEST_ASSERT_TRUE(STAT_HAS_UNCONSUMED_MOCKS(Test_TestStatisticsUponReusableMock));

  for (index = 0, callOrder = 0; index < count; index++)
  {
    STAT_POP_MOCK_WITH_SPYING_NUMERIC(Test_TestSpiedDataUponReusableMock, Stat_Rand());
    STAT_POP_MOCK(Test_TestStatisticsUponReusableMock);
    TEST_ASSERT_EQUAL(++callOrder, STAT_GET_CALL_ORDER(Test_TestSpiedDataUponReusableMock, index));
    TEST_ASSERT_EQUAL(++callOrder, STAT_GET_CALL_ORDER(Test_TestStatisticsUponReusableMock, index));
  }

  TEST_ASSERT_FALSE(STAT_HAS_UNCONSUMED_MOCKS(Test_TestSpiedDataUponReusableMock));
  TEST_ASSERT_FALSE(STAT_HAS_UNCONSUMED_MOCKS(Test_TestStatisticsUponReusableMock));
  STAT_ADD_EMPTY_MOCK(Test_TestSpiedDataUponReusableMock);
  TEST_ASSERT_TRUE(STAT_HAS_UNCONSUMED_MOCKS(Test_TestSpiedDataUponReusableMock));

  for (index = 0; index < count; index++)
  {
    TEST_ASSERT_EQUAL(callOrder - 1, STAT_GET_CALL_ORDER(Test_TestSpiedDataUponReusableMock, index));
    TEST_ASSERT_EQUAL(callOrder, STAT_GET_CALL_ORDER(Test_TestStatisticsUponReusableMock, index));
    TEST_ASSERT_EQUAL_HEX(firstMock, *(_UU32*)STAT_GET_MOCK_DATA(Test_TestSpiedDataUponReusableMock, index));
    TEST_ASSERT_EQUAL_HEX8(secondMock, *(_UU8*)STAT_GET_MOCK_DATA(Test_TestStatisticsUponReusableMock, index));
  }
}

static void Test_TestMixedWithReusableMocks(void)
{
  _UU32 index;
  _UU32 simplePrimitive = Stat_Rand();
  _UU32 count = Stat_RandRange(5, 10);
  _TestMockOject_t reusable = {Stat_Rand(), Stat_Rand()};
  _UU8 simpleLong[] = {0xBB, 0xBE, 0xAF, 0xFA, 0xCE};
  _UU32 reusableSpyData = Stat_Rand();
  _UU32 otherSpyData = Stat_Rand();
  
  STAT_ADD_MOCK(Test_TestMixedWithReusableMocks, simplePrimitive);
  STAT_ADD_REUSABLE_MOCK(Test_TestMixedWithReusableMocks, reusable, count);
  STAT_ADD_MOCK(Test_TestMixedWithReusableMocks, simpleLong);
  STAT_ADD_CALLBACK_MOCK(Test_TestMixedWithReusableMocks, Test_HandleMockCallbackA);
  STAT_OVERRIDE_MOCK(Test_TestMixedWithReusableMocks, Test_OverrideMock);

  TEST_ASSERT_EQUAL_HEX(simplePrimitive, *(_UU32*)STAT_POP_MOCK_WITH_SPYING(Test_TestMixedWithReusableMocks, otherSpyData));
  for (index = 0; index < count; index++)
  {
    TEST_ASSERT_EQUAL_MEMORY(&reusable, 
      STAT_POP_MOCK_WITH_SPYING(Test_TestMixedWithReusableMocks, reusableSpyData), sizeof(reusableSpyData));
  }
  TEST_ASSERT_EQUAL_HEX8_ARRAY(simpleLong, 
    STAT_POP_MOCK_WITH_SPYING(Test_TestMixedWithReusableMocks, otherSpyData), sizeof(simpleLong));
  STAT_POP_MOCK_WITH_SPYING(Test_TestMixedWithReusableMocks, otherSpyData);
  STAT_POP_MOCK_WITH_SPYING(Test_TestMixedWithReusableMocks, otherSpyData);

  TEST_ASSERT_EQUAL(1, STAT_GET_CALL_ORDER(Test_TestMixedWithReusableMocks, 0));
  TEST_ASSERT_EQUAL(count + 1, STAT_GET_CALL_ORDER(Test_TestMixedWithReusableMocks, 1));
  TEST_ASSERT_EQUAL(count + 1, STAT_GET_CALL_ORDER(Test_TestMixedWithReusableMocks, count));
  TEST_ASSERT_EQUAL(count + 2, STAT_GET_CALL_ORDER(Test_TestMixedWithReusableMocks, count + 1));
  TEST_ASSERT_EQUAL(count + 3, STAT_GET_CALL_ORDER(Test_TestMixedWithReusableMocks, count + 2));
  TEST_ASSERT_EQUAL(count + 4, Test_statMock.overrideHandler.callOrder);
  TEST_ASSERT_EQUAL(1, Test_statMock.overrideHandler.callCount);

  TEST_ASSERT_EQUAL_HEX(otherSpyData, *(_UU32*)STAT_GET_MOCK_SPY_DATA(Test_TestMixedWithReusableMocks, 0));
  TEST_ASSERT_EQUAL_HEX(reusableSpyData, *(_UU32*)STAT_GET_MOCK_SPY_DATA(Test_TestMixedWithReusableMocks, count));
  TEST_ASSERT_EQUAL_HEX(otherSpyData, *(_UU32*)STAT_GET_MOCK_SPY_DATA(Test_TestMixedWithReusableMocks, count + 1));
  TEST_ASSERT_EQUAL_HEX(otherSpyData, *(_UU32*)STAT_GET_MOCK_SPY_DATA(Test_TestMixedWithReusableMocks, count + 2));
  TEST_ASSERT_EQUAL_PTR(&otherSpyData, Test_statMock.overrideHandler.dataToSpy_p);
}

static void Test_TestCallbackUponReusableMock(void)
{
  _UU32 mockA = Stat_Rand();
  _UU8 mockB = (_UU8)Stat_Rand();
  _UU32 useCount = Stat_RandRange(20, 30);
  _UU32 spyA = Stat_Rand();
  _UU32 spyB = Stat_Rand();
  _UU32 index;
  
  STAT_ADD_RESUABLE_MOCK_WITH_CALLBACK(Test_TestMixedWithReusableMocks, mockA, useCount, Test_HandleMockCallbackA);
  STAT_ADD_RESUABLE_MOCK_WITH_CALLBACK(Test_TestCallbackUponReusableMock, mockB, useCount, Test_HandleMockCallbackB);

  for (index = 0; index < useCount; index++)
  {
    TEST_ASSERT_EQUAL_HEX(mockA, *(_UU32*)STAT_POP_MOCK_WITH_SPYING(Test_TestMixedWithReusableMocks, spyA));
    TEST_ASSERT_EQUAL_HEX8(mockB, *(_UU8*)STAT_POP_MOCK_WITH_SPYING(Test_TestCallbackUponReusableMock, spyB));
    TEST_ASSERT_EQUAL(index + 1, STAT_COUNT_CALLS(Test_TestMixedWithReusableMocks));
    TEST_ASSERT_EQUAL(index + 1, STAT_COUNT_CALLS(Test_TestCallbackUponReusableMock));
    TEST_ASSERT_EQUAL_HEX(spyA, *(_UU32*)STAT_GET_MOCK_SPY_DATA(Test_TestMixedWithReusableMocks, index));
    TEST_ASSERT_EQUAL_HEX(spyB, *(_UU32*)STAT_GET_MOCK_SPY_DATA(Test_TestCallbackUponReusableMock, index));
  }

  TEST_ASSERT_EQUAL(useCount, Test_statMock.callbackA.callCount);
  TEST_ASSERT_EQUAL((useCount * 2) - 1, Test_statMock.callbackA.callOrder);
  TEST_ASSERT_EQUAL_PTR(STAT_GET_MOCK_DATA(Test_TestMixedWithReusableMocks, 0), Test_statMock.callbackA.mock_p);
  TEST_ASSERT_EQUAL_PTR(STAT_GET_MOCK_SPY_DATA(Test_TestMixedWithReusableMocks, 0), Test_statMock.callbackA.dataToSpy_p);
}

static void Test_TestReusableEmptyMock(void)
{
  _UU32 index;
  _UU32 useCount = Stat_RandRange(15, 27);
  _UU32 spyA = Stat_Rand();
  _UU32 spyB = Stat_Rand();
  _UU32 callOrder = 0;
  
  STAT_ADD_REUSABLE_EMPTY_MOCK(Test_TestReusableEmptyMock, useCount);
  STAT_ADD_REUSABLE_CALLBACK_MOCK(Test_TestReusableEmptyMock, useCount, Test_HandleMockCallbackB);
  
  for (index = 0; index < useCount; index++)
  {
    STAT_POP_MOCK_WITH_SPYING(Test_TestReusableEmptyMock, spyA);
    TEST_ASSERT_EQUAL(++callOrder, STAT_GET_CALL_ORDER(Test_TestReusableEmptyMock, index));
    TEST_ASSERT_NULL(STAT_GET_MOCK_DATA(Test_TestReusableEmptyMock, index));
  }

  for (index = 0; index < useCount; index++)
  {
    STAT_POP_MOCK_WITH_SPYING(Test_TestReusableEmptyMock, spyB);
    TEST_ASSERT_EQUAL(++callOrder, STAT_GET_CALL_ORDER(Test_TestReusableEmptyMock, index + useCount));
    TEST_ASSERT_NULL(STAT_GET_MOCK_DATA(Test_TestReusableEmptyMock, index));
  }

  TEST_ASSERT_EQUAL(useCount, STAT_GET_CALL_ORDER(Test_TestReusableEmptyMock, 0)); 
  TEST_ASSERT_EQUAL((useCount * 2), STAT_GET_CALL_ORDER(Test_TestReusableEmptyMock, useCount)); 
  TEST_ASSERT_EQUAL(useCount, Test_statMock.callbackB.callCount);
  TEST_ASSERT_EQUAL((useCount * 2), Test_statMock.callbackB.callOrder);
  TEST_ASSERT_EQUAL_PTR(STAT_GET_MOCK_DATA(Test_TestReusableEmptyMock, useCount), Test_statMock.callbackB.mock_p);
  TEST_ASSERT_EQUAL_PTR(STAT_GET_MOCK_SPY_DATA(Test_TestReusableEmptyMock, useCount), Test_statMock.callbackB.dataToSpy_p);
}

static void Test_TestReusableMockOverConsumption(void)
{
  _UU32 useCount = Stat_RandRange(25, 37);
  _UU32 index;
  
  STAT_ADD_REUSABLE_EMPTY_MOCK(Test_TestReusableMockOverConsumption, useCount);

  for (index = 0; index < useCount; index++)
  {
    STAT_POP_MOCK(Test_TestReusableMockOverConsumption);
  }
  
  TEST_ABORT_UPON_NON_STAT_MOCK_PERMISSIVE_VALIDATION();
  STAT_POP_MOCK(Test_TestReusableEmptyMock);
  TEST_FAIL_MESSAGE("The test should not reach this point due to expected test-abort!");
}

static void Test_TestReusableMockWithOverflowDueToDataSizeInconsistency(void)
{
  _UU32 useCount = Stat_RandRange(5, 9);
  _UU32 initalSpyData = Stat_Rand();
  _UU8 badSizeSpyData[sizeof(_UU32) + 1] = {(_UU8)-1};
  
  STAT_ADD_REUSABLE_EMPTY_MOCK(Test_TestReusableEmptyMock, useCount);

  STAT_POP_MOCK_WITH_SPYING(Test_TestReusableEmptyMock, initalSpyData);

  TEST_ABORT_UPON_NON_STAT_MOCK_PERMISSIVE_VALIDATION();
  STAT_POP_MOCK_WITH_SPYING(Test_TestReusableEmptyMock, badSizeSpyData);
  TEST_FAIL_MESSAGE("The test should not reach this point due to expected test-abort!");
}

static void Test_TestNonExistingSpyDataExtractionUponReusableMock(void)
{
  _UU32 useCount = Stat_RandRange(10, 20);
  _UU32 index;
  
  STAT_ADD_REUSABLE_EMPTY_MOCK(Test_TestNonExistingSpyDataExtractionUponReusableMock, useCount);

  for (index = 0; index < useCount; index++)
  {
    STAT_POP_MOCK(Test_TestNonExistingSpyDataExtractionUponReusableMock);
  }

  TEST_ASSERT_NULL(STAT_GET_MOCK_SPY_DATA(Test_TestNonExistingSpyDataExtractionUponReusableMock, 0));
  
  TEST_ABORT_UPON_NON_STAT_MOCK_PERMISSIVE_VALIDATION();
  STAT_GET_MOCK_SPY_DATA(Test_TestNonExistingSpyDataExtractionUponReusableMock, useCount);
  TEST_FAIL_MESSAGE("The test should not reach this point due to expected test-abort!");
}

static void Test_TestAddInfiniteMockUponSingleUse(void)
{
  _UU32 mock = Stat_Rand();
  _UU32 spyData = Stat_Rand();
  
  STAT_ADD_INFINITE_MOCK(Test_TestAddInfiniteMockUponSingleUse, mock);

  TEST_ASSERT_TRUE(STAT_HAS_MOCKS(Test_TestAddInfiniteMockUponSingleUse));
  TEST_ASSERT_TRUE(STAT_HAS_UNCONSUMED_MOCKS(Test_TestAddInfiniteMockUponSingleUse));
  TEST_ASSERT_EQUAL(0, STAT_COUNT_CALLS(Test_TestAddInfiniteMockUponSingleUse));

  TEST_ASSERT_EQUAL_HEX(mock, *(_UU32*)STAT_POP_MOCK_WITH_SPYING(Test_TestAddInfiniteMockUponSingleUse, spyData));

  TEST_ASSERT_TRUE(STAT_HAS_UNCONSUMED_MOCKS(Test_TestAddInfiniteMockUponSingleUse));
  TEST_ASSERT_EQUAL(1, STAT_COUNT_CALLS(Test_TestAddInfiniteMockUponSingleUse));
  TEST_ASSERT_EQUAL_HEX(spyData, *(_UU32*)STAT_GET_MOCK_SPY_DATA(Test_TestAddInfiniteMockUponSingleUse, 0));
}

static void Test_TestAddInfiniteMockUponSeveralUses(void)
{
  _UU32 mock = Stat_Rand();
  _UU32 useCount = Stat_RandRange(5, 10);
  _UU32 spyData;
  _UU32 index;
  
  STAT_ADD_INFINITE_MOCK(Test_TestAddInfiniteMockUponSeveralUses, mock);

  for (index = 0; index < useCount; index++)
  {
    spyData = Stat_Rand();
    TEST_ASSERT_EQUAL_HEX(mock, *(_UU32*)STAT_POP_MOCK_WITH_SPYING(Test_TestAddInfiniteMockUponSeveralUses, spyData));
    TEST_ASSERT_EQUAL(index + 1, STAT_COUNT_CALLS(Test_TestAddInfiniteMockUponSeveralUses));
    TEST_ASSERT_EQUAL_HEX(spyData, *(_UU32*)STAT_GET_MOCK_SPY_DATA(Test_TestAddInfiniteMockUponSeveralUses, index));
  }
}

static void Test_TestAddNumericInfiniteMock(void)
{
  _UU32 useCount = Stat_RandRange(3, 17);
  _UU32 spyData;
  _UU32 index;
  
  STAT_ADD_INFINITE_NUMERIC_MOCK(Test_TestAddInfiniteMockUponSeveralUses, 0xFEEDACAD);

  for (index = 0; index < useCount; index++)
  {
    spyData = Stat_Rand();
    TEST_ASSERT_EQUAL_HEX(0xFEEDACAD, *(_UU32*)STAT_POP_MOCK_WITH_SPYING(Test_TestAddInfiniteMockUponSeveralUses, spyData));
    TEST_ASSERT_EQUAL(index + 1, STAT_COUNT_CALLS(Test_TestAddInfiniteMockUponSeveralUses));
    TEST_ASSERT_EQUAL_HEX(spyData, *(_UU32*)STAT_GET_MOCK_SPY_DATA(Test_TestAddInfiniteMockUponSeveralUses, index));
  }
}

static void Test_TestSpiedDataUponInfiniteMock(void)
{
  _UU8 spyData[] = {0xFF, 0xFA, 0xCE, 0xAC, 0xAD, 0xFE, 0xED};
  _UU32 count = sizeof(spyData);
  _UU32 index;
  
  STAT_ADD_INFINITE_NUMERIC_MOCK(Test_TestSpiedDataUponInfiniteMock, Stat_Rand());
  STAT_ADD_INFINITE_NUMERIC_MOCK(Test_TestAddNumericInfiniteMock, Stat_Rand());

  for (index = 0; index < count; index++)
  {
    spyData[index] = count - 1;
    STAT_POP_MOCK_WITH_SPYING(Test_TestSpiedDataUponInfiniteMock, spyData);
    STAT_POP_MOCK(Test_TestAddNumericInfiniteMock);
  }

  for (index = 0; index < count; index++)
  {
    TEST_ASSERT_EQUAL_HEX8_ARRAY(spyData, 
      STAT_GET_MOCK_SPY_DATA(Test_TestSpiedDataUponInfiniteMock, index), count);
    TEST_ASSERT_NULL(STAT_GET_MOCK_SPY_DATA(Test_TestAddNumericInfiniteMock, index));
  }
}

static void Test_TestStatisticsUponInfiniteMock(void)
{
  _UU32 count = Stat_RandRange(7, 17);
  _UU32 index;
  _UU32 callOrder;
  _UU32 firstMock = Stat_Rand();
  _UU8 secondMock = (_UU8)Stat_Rand();
  
  STAT_ADD_INFINITE_MOCK(Test_TestSpiedDataUponInfiniteMock, firstMock);
  STAT_ADD_INFINITE_MOCK(Test_TestStatisticsUponInfiniteMock, secondMock);

  TEST_ASSERT_TRUE(STAT_HAS_MOCKS(Test_TestSpiedDataUponInfiniteMock));
  TEST_ASSERT_TRUE(STAT_HAS_MOCKS(Test_TestStatisticsUponInfiniteMock));

  for (index = 0, callOrder = 0; index < count; index++)
  {
    STAT_POP_MOCK_WITH_SPYING_NUMERIC(Test_TestSpiedDataUponInfiniteMock, Stat_Rand());
    STAT_POP_MOCK(Test_TestStatisticsUponInfiniteMock);
    TEST_ASSERT_EQUAL(++callOrder, STAT_GET_CALL_ORDER(Test_TestSpiedDataUponInfiniteMock, index));
    TEST_ASSERT_EQUAL(++callOrder, STAT_GET_CALL_ORDER(Test_TestStatisticsUponInfiniteMock, index));
  }

  for (index = 0; index < count; index++)
  {
    TEST_ASSERT_EQUAL(callOrder - 1, STAT_GET_CALL_ORDER(Test_TestSpiedDataUponInfiniteMock, index));
    TEST_ASSERT_EQUAL(callOrder, STAT_GET_CALL_ORDER(Test_TestStatisticsUponInfiniteMock, index));
    TEST_ASSERT_EQUAL_HEX(firstMock, *(_UU32*)STAT_GET_MOCK_DATA(Test_TestSpiedDataUponInfiniteMock, index));
    TEST_ASSERT_EQUAL_HEX8(secondMock, *(_UU8*)STAT_GET_MOCK_DATA(Test_TestStatisticsUponInfiniteMock, index));
  }
}

static void Test_TestInfiniteEmptyMock(void)
{
  _UU32 index;
  _UU32 useCount = Stat_RandRange(5, 27);
  _UU32 spyA = Stat_Rand();
  _UU32 spyB = Stat_Rand();
  _UU32 callOrder = 0;
  
  STAT_ADD_INFINITE_EMPTY_MOCK(Test_TestInfiniteEmptyMock);
  
  for (index = 0; index < useCount; index++)
  {
    STAT_POP_MOCK_WITH_SPYING(Test_TestInfiniteEmptyMock, spyA);
    TEST_ASSERT_EQUAL(++callOrder, STAT_GET_CALL_ORDER(Test_TestInfiniteEmptyMock, index));
    TEST_ASSERT_NULL(STAT_GET_MOCK_DATA(Test_TestInfiniteEmptyMock, index));
  }

  TEST_ASSERT_EQUAL(callOrder, STAT_GET_CALL_ORDER(Test_TestInfiniteEmptyMock, 0)); 
  TEST_ASSERT_EQUAL(callOrder, STAT_GET_CALL_ORDER(Test_TestInfiniteEmptyMock, useCount - 1)); 
}

static void Test_TestInfiniteCallbackMock(void)
{
  _UU32 index;
  _UU32 useCount = Stat_RandRange(5, 27);
  _UU32 spyA = Stat_Rand();
  _UU32 spyB = Stat_Rand();
  _UU32 callOrder = 0;
  
  STAT_ADD_INFINITE_CALLBACK_MOCK(Test_TestInfiniteCallbackMock, Test_HandleMockCallbackA);
  
  for (index = 0; index < useCount; index++)
  {
    STAT_POP_MOCK_WITH_SPYING(Test_TestInfiniteCallbackMock, spyA);
    TEST_ASSERT_EQUAL(++callOrder, STAT_GET_CALL_ORDER(Test_TestInfiniteCallbackMock, index));
    TEST_ASSERT_NULL(STAT_GET_MOCK_DATA(Test_TestInfiniteCallbackMock, index));
  }

  TEST_ASSERT_EQUAL(callOrder, STAT_GET_CALL_ORDER(Test_TestInfiniteCallbackMock, 0)); 
  TEST_ASSERT_EQUAL(callOrder, STAT_GET_CALL_ORDER(Test_TestInfiniteCallbackMock, useCount - 1)); 

  TEST_ASSERT_EQUAL(useCount, Test_statMock.callbackA.callCount);
  TEST_ASSERT_EQUAL(callOrder, Test_statMock.callbackA.callOrder);
  TEST_ASSERT_EQUAL_PTR(STAT_GET_MOCK_DATA(Test_TestInfiniteCallbackMock, 0), Test_statMock.callbackA.mock_p);
  TEST_ASSERT_EQUAL_PTR(STAT_GET_MOCK_SPY_DATA(Test_TestInfiniteCallbackMock, 0), Test_statMock.callbackA.dataToSpy_p);
}

// 7
// TODO: static void Test_TestMixedWithInfiniteMocks(void);
// TODO: static void Test_TestInfiniteMockWithOverflowDueToDataSizeInconsistency(void);
// TODO: static void Test_TestNonExistingSpyDataExtractionUponInfiniteMock(void);


static void Test_SetupTest(void)
{
  Stat_Memset(&Test_statMock, 0, sizeof(Test_statMock));
  Stat_SetupMock();
}

static void Test_TearDownTest(void)
{
  Stat_SetupMock();
}

static void Test_HandleMockCallbackA(_UU32 callOrder, void* mock_p, void* dataToSpy_p)
{
  Test_SpyOnTestCallbackCall(callOrder, mock_p, dataToSpy_p, &Test_statMock.callbackA);
}

static void Test_HandleMockCallbackB(_UU32 callOrder, void* mock_p, void* dataToSpy_p)
{
  Test_SpyOnTestCallbackCall(callOrder, mock_p, dataToSpy_p, &Test_statMock.callbackB);
}

static void Test_SpyOnTestCallbackCall(_UU32 callOrder, void* mock_p, void* dataToSpy_p, _TestCallbackSpy_t *spy_p)
{
  spy_p->callCount++;
  spy_p->callOrder = callOrder;
  spy_p->mock_p = mock_p;
  spy_p->dataToSpy_p = dataToSpy_p;
}

static void Test_EnforceCallOrderTracking(_UU32 callOrder, void* mock_p, void* dataToSpy_p)
{
  STAT_ENFORCE_CALL_ORDER_TRACKING();
}

static void Test_CeaseCallOrderTracking(_UU32 callOrder, void* mock_p, void* dataToSpy_p)
{
  STAT_CEASE_CALL_ORDER_TRACKING();
}

static void* Test_OverrideMock(_UU32 callOrder, _UU32 callCount, const void* dataToSpy_p)
{
  Test_statMock.overrideHandler.callOrder = callOrder;
  Test_statMock.overrideHandler.callCount = callCount;
  Test_statMock.overrideHandler.dataToSpy_p = dataToSpy_p;
  return (void*)Test_statMock.overrideHandler.mock_p;
}

/******************************************************************************/
/**    END OF FILE                                                           **/
/******************************************************************************/

