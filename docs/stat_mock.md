# STAT-Mock Library

## Overview

STAT-Mock is a built-in library of the STAT framework, which allows a 
convenient way to create, manipulate and utilize test-doubles (e.g. 
mocks, spies) along with collection of related statistics. 
The library provides a very simple API set. It can be used to create a 
variety of test-double types, to program mock-driven to build specific 
test flows and of course to assert the validity of captured statistics. 
Each of the specified operations can be achieved by a simple macro-call.   
STAT-Mock was designed with mindset set to follow the _Four-Phase Test_ 
testing pattern:

1. Setup test
2. Exercise CUT
3. Verify results/outputs
4. Teardown  

The fist three phases are straightforward and intuitive and for each
one STAT-Mock provides a dedicated set of API macros:

* A set of macros to program mock-objects for the Setup phase
* A set of macros to implement test-doubles for the Exercise-CUT phase
* A set of macros to extract the spied data and the collected statistics

The forth phase like in many other unit-testing frameworks is resolved
by the STAT-Mock library implicitly. The state of the library database 
always gets cleared between any two adjacent unit-tests. 
However, in STAT-Mock the forth phase is implemented instead of 
the teardown stage during the setup stage before each test.

## Enabling STAT-Mock

Enabling of STAT-Mock library is quite simple and straightforward. 
One needs simply to add the following definition to the makefile:
```c
STAT_MOCK = <byte-size of RAM to use>
```

>Note that STAT-Mock can be enabled either on the product level (i.e. 
>in the product makefile) or on the test-package level (i.e. in 
>the test-package makefile). The latter allows different RAM-size
>allocations, per test-package.
  
STAT-Mock library is optimized for the minimal resource requirements to 
suite possible migration to embedded environment in future to support 
unit-testing on the target platform. Therefore, the framework allows to 
define the RAM allocation that is allowed to spend on STAT-Mock database.
    
>It is important to note that if the user chooses to define the size 
>above ***8 KByte***, the database will consume more memory for the 
>metadata of each entry in order to be able to deal with the bigger RAM 
>space.

## Mock-Usage Validation

STAT-Mock by default validates the creation and the consumption of the 
test-doubles and of the collectibles, and fails the test upon related 
exceptions. For instance, if a test declares a mock-object creation but 
the tested CUT doesn't produce a call that shall consume the mock-object, 
the test will fail. The framework also prints an error message that 
refers to the unconsumed mock-object. This validation can be put into a 
permissive mode (aborting test instead of failing) by the following 
definition:
```c
STAT_MOCK_PERMISSIVE_VALIDATION
```     

## Terms and Parameters

The following terms for STAT-Mock parameters are used throughout the sources of this framework 
(including this documentation):
- @param **declarator** - a string with the name of the related declaration (e.g.function-name);
                          used as a key to distinguish objects of different test-doubles
- @param **mock** - a variable/structure representing a Mock-object
- @param **numeric-mock** - a numeric value (e.g. constant) representing a Mock-object
- @param **callback** - a function to be called when a related Mock object is popped
- @param **handler** - a function called instead of Mock-engine to produce a Mock object and to spy
- @param **data-to-spy** - a variable/structure to be spied for further verification in the test
- @param **spy-data** - (see data-to-spy)
- @param **numeric-to-spy** - a numeric value spied for further verification in the test
- @param **creation-index** - a 0-based counter representing an order in which the item was  created for the declarator
- @param **call-order** - an 1-based counter representing an order in which the call was issued
                          for this entry in reference to all other call (of all declarators)
- @param **call-count** - an amount of accesses made to the object during the test
- @param **test-callable** - any callable object, including mocks and pure spy-data (without a mock)

## Callbacks

API set of STAT-Mock assumes two types of possible callbacks that the user might feed the framework with.  

The first type of callbacks is used a complimentary operation that the user asks 
the framework to invoke upon consumption of a certain mock-object. 
The goal of such callback is only to observe/modify the data that the framework has collected 
at that moment of consumption. Such callback shall have the following signature:

```c
void (*STAT_MOCK_CALLBACK_T)(_UU32 callOrder, void* mock_p, void* dataToSpy_p);
```

The second type is not meant just to process the data collected by the framework, 
but to override the behavior of a test-double that was originally defined
as mock-object. The data that is passed by the framework to this callback is not
a copy of the CUT data (like it is in the case with the previous callback). 
It receives the original data of the caller and thus is passed as constant. 
Such handler shall have the following signature:

```c
void* (*STAT_MOCK_HANDLER_T)(_UU32 callOrder, _UU32 callCount, const void* dataToSpy_p);
```

Every data (i.e. mock, data-to-spy) passed to these macros is passed by value and copied
into the internal database of STAT-Mock. When it is retrieved back, this copy is passed
to the caller by pointer. If one wants to prevent the copying, he/she should pass a pointer
to the data instead of the data itself. It is important to note, though, that in this case that 
upon retrieval a pointer to a pointer is returned.

## STAT-Mock APIs 

## Behavioral Macros

This set of APIs is intended to control the behavior of the STAT-Mock library.

* `STAT_RESET()` - clears the entire database of STAT-Mock
* `STAT_ENFORCE_CALL_ORDER_TRACKING` and `STAT_CEASE_CALL_ORDER_TRACKING`
    * These two macros define a scope in which all calls made by CUT 
    to mock-driven test-doubles are expected to be in order, 
    in which the mock-objects where created.
    * It's useful in testing of pieces of code that implement a sequence
    of actions. It allows a simple validation of the order of calls
  
## Setup-Phase Macros

This set of APIs is designed for the Setup phase of the Four-Phase Test pattern.
It comprises the macros which allow creation of different types of Mock-objects.

* `STAT_ADD_MOCK(_declarator_, _mock_)` 
* `STAT_ADD_MOCK_WITH_CALLBACK(_declarator_, _mock_, _callback_)` 
* `STAT_ADD_NUMERIC_MOCK(_declarator_, _numeric_mock_)` 
* `STAT_ADD_NUMERIC_MOCK_WITH_CALLBACK(_declarator_, _numeric_mock_, _callback_)` 
* `STAT_ADD_EMPTY_MOCK(_declarator_)` 
* `STAT_ADD_CALLBACK_MOCK(_declarator_, _callback_)` 
* `STAT_ADD_MANY_MOCKS(_declarator_, _mocks_ptr_, _mock_amount_)` 
* `STAT_ADD_MANY_MOCKS_WITH_CALLBACK(_declarator_, _mocks_ptr_, _mock_amount_, _callback_)` 
* `STAT_ADD_REUSABLE_EMPTY_MOCK(_declarator_, _use_count_)` 
* `STAT_ADD_REUSABLE_CALLBACK_MOCK(_declarator_, _use_count_, _callback_)` 
* `STAT_ADD_REUSABLE_MOCK(_declarator_, _mock_, _use_count_)` 
* `STAT_ADD_RESUABLE_MOCK_WITH_CALLBACK(_declarator_, _mock_, _use_count_, _callback_)` 
* `STAT_ADD_REUSABLE_NUMERIC_MOCK(_declarator_, _mock_, _use_count_)` 
* `STAT_ADD_REUSABLE_NUMERIC_MOCK_WITH_CALLBACK(_declarator_, _mock_, _use_count_, _callback_)` 
* `STAT_OVERRIDE_MOCK(_declarator_, _handler_)` 

## 'Exercise-CUT'-Phase Macros

This set of APIs is designed for the Exercise-CUT phase of the Four-Phase Test pattern.
As the matter of fact, though officially this phase is a second one in this test-pattern,
the set of this phase is the first one to be used by the developer.
These macros are used to implement the test-doubles themselves, 
which are usually implemented before the tests and CUT.

* `STAT_POP_MOCK(_declarator_)` 
* `STAT_POP_MOCK_WITH_SPYING(_declarator_, _data_to_spy_)` 
* `STAT_POP_MOCK_WITH_SPYING_NUMERIC(_declarator_, _numeric_to_spy_)` 
* `STAT_SPY_ON_WITHOUT_MOCK(_declarator_, _data_to_spy_)` 
* `STAT_SPY_ON_NUMERIC_WITHOUT_MOCK(_declarator_, _numeric_to_spy_)` 

## Verification-Phase Macros

This set of APIs is designed for the Verify phase of the Four-Phase Test pattern.
These macros are used by the developer to extract the collected data (e.g. spied-data) 
and the statistics (e.g different counters).

* `STAT_GET_MOCK_DATA(_declarator_, _creation_index_)` 
* `STAT_GET_MOCK_SPY_DATA(_declarator_, _creation_index_)` 
* `STAT_GET_CALL_ORDER(_declarator_, _creation_index_)` 
* `STAT_COUNT_CALLS(_declarator_)` 
* `STAT_COUNT_TEST_CALLABLES(_declarator_)` 
* `STAT_HAS_MOCKS(_declarator_)` 
* `STAT_HAS_UNCONSUMED_MOCKS(_declarator_)` 
