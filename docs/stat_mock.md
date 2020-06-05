# STAT-Mock Library

## Introduction

STAT-Mock is a built-in library of the STAT framework, which allows a 
convenient way to create, manipulate and utilize test-doubles (e.g. 
mocks, spies) along with collection of related statistics. 

The library provides an API set to implement test-doubles of variety 
of types, to program mock-driven test-doubles and to retrieve for
validity assertion the data that was collected along the test:  

* Each of the specified actions is performed with a simple macro-call.
* All actions use a common time-scale, with all the benefits 
    for validity assertion that it can provide

### Overview

#### *Four-Phase Test-Pattern*

STAT-Mock is designed with mindset set to follow the *Four-Phase Test 
pattern*:

1. Setup test
2. Exercise CUT
3. Verify results/outputs
4. Teardown  

Each of the first three phases is represented in the library by a 
dedicated set of API macros:

1. A set of macros to program mock-objects for the Setup phase
2. A set of macros to implement test-doubles for the Exercise-CUT phase
3. A set of macros to extract the data spied along the test

The fourth phase is implemented by the library itself, using the 
test-setup/test-teardown facility of the STAT framework.

#### *Test-Double Types*

The library supports implementation of test-doubles of the following
types:
* Pure Mocks
* Pure Spies
* Combination of these two, with one another, 
    or with other primitive types

>Please refer to [*Theoretical Background*](stat_theoretical_background.md)
>to learn about the benefits and specifics of each of the types

#### *Callbacks*
The library has a built-in mechanism that allows callback-feeding 
for any Mock-driven test-doubles.

#### *Collected Data and Statistics*

STAT-Mock collects some useful statistics that can be retrieved and
validated.

The data that is collected via the API macros of the library is 
copied to the internal RAM-buffer of the library. The user doesn't
have to store this data if its scope is left. Therefore:
* Data shall be passed to the macros by value
    * If a pointer is passed, only a pointer will be copied
* Upon retrieval a pointer to the copied data is returned
    * If a pointer was stored, a pointer-to-pointer is returned 

### Enabling STAT-Mock

Enabling of STAT-Mock library is quite simple and straightforward. 
One needs simply to add the following definition to the makefile:
```c
STAT_MOCK = <byte-size of RAM to use>
```

>Note that STAT-Mock can be enabled either on the product level (i.e. 
>in the product makefile) or on the test-package level (i.e. in 
>the test-package makefile). 
>The latter allows different RAM-budgets per test-package.
  
STAT-Mock library is optimized for the minimal resource requirements to 
suite possible migration to embedded environment in future to support 
unit-testing on the target platform. Therefore, the framework doesn't 
use facilities like `malloc`. Instead, it manages it's own RAM buffer,
the size of which is set upon enabling of the library.
    
>It is important to note that if the user chooses to define the size 
>above ***8 KByte***, the database will consume more memory for the 
>metadata of each entry in order to be able to deal with the bigger RAM 
>space.

>Note that the RAM-buffer size cannot be bigger than *512 KByte*.

### Mock-Usage Validation

STAT-Mock by default validates the creation and the consumption of the 
mock-objects:
* It asserts that all created mock-objects are consumed, 
    and by default fails the test if not 
* This validation can be put into a permissive mode
    * In this case the test will have status 'Aborted' instead of 'Failed'
    * To turn this mode one shall add to definitions of the makefile 
    the `STAT_MOCK_PERMISSIVE_VALIDATION` toggle

## APIs

### Terms and Parameters

The following terms for STAT-Mock parameters are used throughout the sources of this framework 
(including this documentation):
- `declarator` - a string with the name of the related declaration (e.g.function-name);
                 used as a key to distinguish objects of different test-doubles
- `mock` - a variable/structure representing a Mock-object
- `numeric-mock` - a numeric value (e.g. constant) representing a Mock-object
- `callback` - a function to be called when a related Mock object is popped
- `handler` - a function called instead of Mock-engine to produce a Mock object and to spy
- `data-to-spy` - a variable/structure to be spied for further verification in the test
- `spy-data` - (see `data-to-spy`)
- `numeric-to-spy` - a numeric value spied for further verification in the test
- `creation-index` - a 0-based counter representing an order in which the item was  created for the `declarator`
- `call-order` - an 1-based counter representing an order in which the call was issued
                 for this entry in reference to all other call (of all `declarators`)
- `call-count` - an amount of accesses made to the object during the test
- `test-callable` - any callable object, including mocks and pure `spy-data` (without a mock)

### Callback Types

API set of STAT-Mock assumes two types of possible callbacks that the user might feed the framework with.  

#### *Complimentary*

The first type of callbacks is used a complimentary operation that the user asks 
the framework to invoke upon consumption of a certain mock-object. 
The goal of such callback is only to observe/modify the data that the framework has collected 
at that moment of consumption. Such callback shall have the following signature:

```c
void (*STAT_MOCK_CALLBACK_T)(_UU32 callOrder, void* mock_p, void* dataToSpy_p);
```

#### *Overloading*

The second type of callbacks overrides the default behavior of a 
mock-driven test-double. Since it acts as a test-double handler, 
the data that is passed by the framework to this callback is the 
original CUT data, unlike with the complimentary callback. 
The handler shall have the following signature:

```c
void* (*STAT_MOCK_HANDLER_T)(_UU32 callOrder, _UU32 callCount, const void* dataToSpy_p);
```

### Behavioral APIs

This set of APIs is intended to control the behavior of the STAT-Mock library.

* `STAT_RESET()` - clears the entire database of STAT-Mock
* `STAT_ENFORCE_CALL_ORDER_TRACKING` and `STAT_CEASE_CALL_ORDER_TRACKING`
    * These two macros define a scope in which all calls made by CUT 
    to mock-driven test-doubles are expected to be in order, 
    in which the mock-objects where created.
    * It's useful in testing of pieces of code that implement a sequence
    of actions. It allows a simple validation of the order of calls
  
### *Setup-Phase* APIs

This set of APIs is designed for the Setup phase of the Four-Phase Test pattern.
It comprises the macros which allow creation of different types of Mock-objects.

* To create a single mock-object for a mock-driven test-double:
    * `STAT_ADD_MOCK(_declarator_, _mock_)` 
    * `STAT_ADD_MOCK_WITH_CALLBACK(_declarator_, _mock_, _callback_)` 
    * `STAT_ADD_NUMERIC_MOCK(_declarator_, _numeric_mock_)` 
    * `STAT_ADD_NUMERIC_MOCK_WITH_CALLBACK(_declarator_, _numeric_mock_, _callback_)` 
    * `STAT_ADD_EMPTY_MOCK(_declarator_)` 
    * `STAT_ADD_CALLBACK_MOCK(_declarator_, _callback_)` 
* To create many mock-objects for a mock-driven test-double:  
    Could be useful for loops of CUT:
    * `STAT_ADD_MANY_MOCKS(_declarator_, _mocks_ptr_, _mock_amount_)` 
    * `STAT_ADD_MANY_MOCKS_WITH_CALLBACK(_declarator_, _mocks_ptr_, _mock_amount_, _callback_)` 
* To create a mock-object that shall be consumed more then once:  
    Could be useful for loops of CUT:
    * `STAT_ADD_REUSABLE_EMPTY_MOCK(_declarator_, _use_count_)` 
    * `STAT_ADD_REUSABLE_CALLBACK_MOCK(_declarator_, _use_count_, _callback_)` 
    * `STAT_ADD_REUSABLE_MOCK(_declarator_, _mock_, _use_count_)` 
    * `STAT_ADD_RESUABLE_MOCK_WITH_CALLBACK(_declarator_, _mock_, _use_count_, _callback_)` 
    * `STAT_ADD_REUSABLE_NUMERIC_MOCK(_declarator_, _mock_, _use_count_)` 
    * `STAT_ADD_REUSABLE_NUMERIC_MOCK_WITH_CALLBACK(_declarator_, _mock_, _use_count_, _callback_)` 
* To override a mock-driven test-double with a proprietary handler:
    * `STAT_OVERRIDE_MOCK(_declarator_, _handler_)` 

### *'Exercise-CUT' Phase* Macros

This set of APIs is designed for the Exercise-CUT phase of the Four-Phase Test pattern.
As the matter of fact, though officially this phase is a second one in this test-pattern,
the set of this phase is the first one to be used by the developer.
These macros are used to implement the test-doubles themselves, 
which are usually implemented before the tests and CUT.

* To implement a pure-spy test-double:
    * `STAT_SPY_ON_WITHOUT_MOCK(_declarator_, _data_to_spy_)` 
    * `STAT_SPY_ON_NUMERIC_WITHOUT_MOCK(_declarator_, _numeric_to_spy_)` 
* To implement a pure-mock test-double:  
    *(returns a pointer to the next unconsumed mock-object)*
    * `STAT_POP_MOCK(_declarator_)` - 
* To implement a mock-driven test-double combined with spying:  
    *(return a pointer to the next unconsumed mock-object)* 
    * `STAT_POP_MOCK_WITH_SPYING(_declarator_, _data_to_spy_)` 
    * `STAT_POP_MOCK_WITH_SPYING_NUMERIC(_declarator_, _numeric_to_spy_)` 

### *Verification-Phase* Macros

This set of APIs is designed for the Verify phase of the Four-Phase Test pattern.
These macros are used by the developer to extract the collected data (e.g. spied-data) 
and the statistics (e.g different counters).

* Get data spied during the test-run:  
  *(return a pointer to the data spied upon call made at specified index)*  
    * `STAT_GET_MOCK_DATA(_declarator_, _creation_index_)` - 
        returns a pointer to the mock-object created for the call given by index
    * `STAT_GET_MOCK_SPY_DATA(_declarator_, _creation_index_)` - 
        returns a pointer to the data spied upon call given by index
* Get statistics collected during the test-run:
    * `STAT_GET_CALL_ORDER(_declarator_, _creation_index_)` 
    * `STAT_COUNT_CALLS(_declarator_)` 
    * `STAT_COUNT_TEST_CALLABLES(_declarator_)` 
* Get-status APIs
    * `STAT_HAS_MOCKS(_declarator_)` 
    * `STAT_HAS_UNCONSUMED_MOCKS(_declarator_)` 

## Examples

### Pure-Spy Test-Double

Following APIs should be used:
* `STAT_SPY_ON_WITHOUT_MOCK()` - to implement a test-double
* `STAT_GET_MOCK_SPY_DATA()` - to get data spied during a specific call

Lets assume we have a CUT function `void Cut_DoSomeWork(...)` which 
depends on DOC `void Doc_LogEvent(_UU32 eventCode)`.

The pure-spy test-double for such DOC can be implemented as follows:
```c
void Doc_LogEvent(_UU32 eventCode)
{
  STAT_SPY_ON_WITHOUT_MOCK(Doc_LogEvent, eventCode);
}
```

Assume that the final implementation of `Cut_DoSomeWork` 
makes two call to this DOC:
```c
void Cut_DoSomeWork(...)
{
  ...
  Doc_LogEvent(DOC_EVENT_A);
  ...
  Doc_LogEvent(DOC_EVENT_B);
  ...
}
```

In this case the test for this function could have the following 
implementation:
```c
static void Test_TestSomeWork(void)
{
  _UU32 received;
  ...

  Cut_DoSomeWork(...); // Exercise CUT, which calls that DOC 
  ...
  ...

  // Verify spied data for each of the DOC calls
  received = *(_UU32*)STAT_GET_MOCK_SPY_DATA(Doc_LogEvent, 0);
  TEST_ASSERT_EQUAL_HEX(DOC_EVENT_A, received);
  received = *(_UU32*)STAT_GET_MOCK_SPY_DATA(Doc_LogEvent, 1);
  TEST_ASSERT_EQUAL_HEX(DOC_EVENT_B, received);
  ...
}
```

### Mock-Driven Test-Double

Following APIs should be used:
* `STAT_POP_MOCK_WITH_SPYING()` - to implement a test-double
* `STAT_ADD_NUMERIC_MOCK()` - to create mock-object for the test-double to consume
* `STAT_GET_MOCK_SPY_DATA()` - to get data spied during a specific call

Lets assume we have a CUT function `void Cut_DoSomeWorkOnData(...)` which 
depends on DOC `void Doc_GetDataSize(...)`.

The mock-driven test-double might have the following implementation:
```c
_UU32 Doc_GetDataSize(const void *payload_p)
{
  return *(_UU32*)STAT_POP_MOCK_WITH_SPYING(Doc_GetDataSize, payload_p);
}
```

Assume that the final implementation of `Cut_DoSomeWorkOnData` 
makes a single call to this DOC. The return value of the DOC
defines which flow within CUT is taken:
```c
void Cut_DoSomeWorkOnData(const void *payload_p, ...)
{
  ...
  size = Doc_GetDataSize(payload_p);
  if (size != 0)
  {
    ... // flow (a)
  }
  else
  {
    ... // flow (b)
  }
  ...
}
```

In this case the test for this function could have the following 
implementation:
```c
static void Test_TestSomeZeroSizeCase(void)
{
  void** received_p;
  _UU8 buffer[CUT_PAYLOAD_SIZE];
  ...
  ... 
  // Setup mock-objects for the test
  STAT_ADD_NUMERIC_MOCK(Doc_GetDataSize, 0);

  Cut_DoSomeWorkOnData(buffer, ...); // Exercise CUT over flow (b)
  ...
  
  // Validate the data spied on that call
  received_p = STAT_GET_MOCK_SPY_DATA(Doc_GetDataSize, 0);
  TEST_ASSERT_EQUAL_PTR(buffer, *received_p);
  ...
}
```

### Complimentary Callbacks

This example shows an example of testing asynchronous logic.

Following APIs will be used:
* `STAT_ADD_EMPTY_MOCK()` - 
    to create `NULL` mock-object used in test for flow control only 
* `STAT_ADD_CALLBACK_MOCK()` -
    to create `NULL` mock-object and to emulate asynchronous activity
    
Let's assume we have a CUT function that is looping with sleeping
until a global variable `Cut_isDone` changes to `TRUE`:
```c
void Cut_DoSomething(...)
{
  ...
  while (Cut_isDone == FALSE)
  {
    ...
    Os_Sleep(1);
  }
  ...
}
```

Let's assume the following implementation of the test-double 
for DOC-function `Os_Sleep(...)`: 
```c
void Os_Sleep(_UU32 timeInMsec)
{
  STAT_POP_MOCK_WITH_SPYING(Os_Sleep, timeInMsec);
}
```

The callback that is supposed to break the loop might 
have the following implementation:
```c
void Test_SetDone(_UU32 order, void* mock_p, void* spy_p)
{
  Cut_isDone = TRUE;
}
```

The test that could have tested the argued loop-logic within 
th given CUT function might have the following implementation.
```c
static void Test_TestSomething(void)
{
  ...
  // The loop within CUT will cycle trice and then will exit
  STAT_ADD_EMPTY_MOCK(Os_Wait);
  STAT_ADD_EMPTY_MOCK(Os_Wait);
  STAT_ADD_CALLBACK_MOCK(Os_Wait, Test_SetDone);
  ...
  Cut_DoSomething(...); // Calls DOC API
  ...
}
```

>All the examples given in this documentation do not exhaust 
>all the possibilities of the library.