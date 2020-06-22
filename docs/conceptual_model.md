# Conceptual Model <!-- omit in toc -->

## Table of Contents <!-- omit in toc -->

- [1. Background](#1-background)
  - [1.1. Problem Statement](#11-problem-statement)
  - [1.2. Technical Issues](#12-technical-issues)
  - [1.3. Not so Technical Issues](#13-not-so-technical-issues)
  - [1.4. Technicalities](#14-technicalities)
  - [1.5. Strategy](#15-strategy)
- [2. Concepts](#2-concepts)
  - [2.1. Reverse Polymorphism by Compilation](#21-reverse-polymorphism-by-compilation)
  - [2.2. Dummy Interfaces](#22-dummy-interfaces)
  - [2.3. CUT Isolation](#23-cut-isolation)
- [3. Unit-testing Model](#3-unit-testing-model)
  - [3.1. Test-Package Model](#31-test-package-model)
  - [3.2. Test-Doubles](#32-test-doubles)
  - [3.3. Callbacks](#33-callbacks)
  - [3.4. Code-Sharing Model](#34-code-sharing-model)
- [4. Summary](#4-summary)

## 1. Background

### 1.1. Problem Statement

It's quite common in the industry that a codebase does not change dramatically in a time-frame of a single project. The changes are rather local in nature and tones of legacy code are dragged from one project to another.  
With the embedded products the challenge gets even harder, since these are not pure software solutions, but usually include many HW cores with interfaces that don't act exactly the same way as of software.  
In addition, embedded environment usually has many constraints, like memory-size, code-size, low CPU power, etc. These ones complicate the conditions for such great programming practices as TDD. At least, we found it hard to convince some embedded-SW developers (especially veterans) that TDD is practical in these conditions. Convincing managers is even harder. One needs to practice TDD and thus obtain the evidence of its benefit, in order to get managerial approval and support to practice it. What's a conundrum?  

### 1.2. Technical Issues

During the research we found out that there were already several attempts in some other groups of our company to apply the TDD methodology. Unfortunately, those were not successful. Our first trials were no good either. Even unit-testing itself (not mandatory TDD) was quite tough. The unit-tests became overcomplicated with time, which made them too fragile and sensitive to changes. Changing code or unit-test in one place, was always breaking unit-tests in a completely different part of the code. This resulted mainly by dependencies, which usually are much bigger in numbers than one could originally think of.

Dealing with dependencies is especially challenging with the programming languages like C, due to following constraints:

* No inherent tools like Interface to formalize and fixate APIs
* No function overloading (or default argument-values) to extend the existing APIs,  
  and (perhaps most important) 
* No real support of dynamic polymorphism or any kind for that matter 

>Though the latter perhaps could be resolved with the callbacks, which requires strong commitment from all the development teams involved.
But the worst thing with the callbacks that one might find it very difficult to persuade especially those veterans of Embedded that 
FW-overhead of callbacks does totally worth the benefit of having TDD. 

### 1.3. Not so Technical Issues

As with any methodology human factor has significant challenges:

* It takes time to accept the mindset of "*tests drive the development*"
* It takes time to educate and to assimilate TDD into the workflow
* Not everybody is willing to commit and/or to follow the methodology
    * Many teams &rArr; many ideologies/approaches/opinions
* Not all developers are equally skilled at unit-testing, at least not at the very beginning

### 1.4. Technicalities

Once shall understand that the issues listed above have to be solved somehow we have actually persuaded the system (the management) to support TDD. Moreover, one shall take into account that there are lots of non-compliant legacy code, but there is no one yet willing to allow touching it seemingly for no justifiable reason.  
Now, Alice can imagine how deep the whole really is! 

### 1.5. Strategy

We understood that the best way to make others follow is to start our own initiative without requesting from others to comply. To achieve this goal, first, we need to ensure some sort of isolation-sphere for the development of the TDD-compliant "isles" within the "sea" of the legacy non-compliant codebase.  
Even after the isles will take over and "dry up" the sea, with only few lakes of legacy-code left, still such "isolation" would provide flexibility and independence of development efforts. Actually, if one follows the idea, one can see the similarities with the concept of [***microservices***](https://microservices.io/). 

## 2. Concepts

<!-- TODO: Introduce Seams (Michael Feathers: A seam is a place where you can alter behavior in your program without editing in that place -->

### 2.1. Reverse Polymorphism by Compilation

Unlike many OO languages, C doesn't have an inherent methods of implementing dynamic polymorphism. But, dynamic polymorphism is a strong tool that allows substitution of product versions of DOCs with test-doubles.   
Of course we can achieve the same effect with the manual workaround. We can implicitly implement the `vTable` and initialize it with callback functions either of production code or of test-doubles. Sounds like a good solution, but there are several problems with this method though:

* In embedded environment function pointers many times are not an option 
    * It might produce unacceptable overhead penalty
    * It forces limits on the usage of inline functions and macros
* This method also assumes that all DOCs comply 
    * It is not the cases for us, and it canned be enforced (as it was explained above)
* The stated conditions also assume tones of legacy code, which doesn't comply by definition
* And in general, any method that cannot be forced by language might become a fragile liability 

Then, the next best thing would be static polymorphism. But it has many of the weak-points that we already pointed out for the dynamic polymorphism.

Eventually, we solved the issue with some sort of *Reverse Polymorphism by Compilation*. 

Many header files (that in C serve some sort of interfaces) are "contaminated" with partial implementations, e.g. inline functions, macros. Even if had enforced a methodology of constraining the header files from having any implementation-specific data, still we would have had a problem with the legacy headers. There are too many of those and we can't touch them in our case. Moreover, this is not something that you can enforce in C and thus,
it would be hard to maintain and to ensure especially in a big-scale projects with a cross-sites team.

### 2.2. Dummy Interfaces

Instead of constraining the header files we instruct developers to create a header-file prototype for DOC API header-files if needed. The former would be a very simplified version of the latter. We named it *Dummy Interface*. It works as if a *Dummy Interface* was a real Interface from which the related DOC derives its implementation. *Dummy Interface* contains no implementation, e.g.:

* Each inline is substituted with non-inline prototype
* Each macro is redirected to a non-inline function of similar name

Note that the *Dummy Interface* doesn't have to contain every object that the original function does. The developers are instructed to work similar to open-source community - each developer adds to a given *Dummy Interface* only what he/she needed. The other developers will add the rest upon demand.

STAT framework has built-in mechanisms that allow simple overriding of original header files with their *Dummy Interface* versions, either for all test-packages at once, or for each test-package separately.

#### 2.2.1. *Public Dummy Interfaces*

STAT supports this approach by providing a dedicated method of maintaining *Dummy Interfaces* in a centralized location (to prevent excessive duplication) and overrides a real header file, if such one appear on an include path of the unit-test package.

As noted above, each dummy interface explicitly declared for the given test-package overrides any other instance of the header files of the same name, whether such one can or cannot be located on the include path.

#### 2.2.2. *Private Dummy Interfaces*

In addition to DOC public APIs, there is a need to substitute certain internal header-files too. For instance, this could be a header-file designed as a *facade* intended to decouple the given CUT from certain system components.  
It makes sense to place dummy interfaces of public APIs in a single central location which is accessible to all test-packages, as it helps to reduce duplication. Whereas, dummy interfaces of internal APIs should be kept locally for each test package, as these are less likely to be accessed by other test-packages. 
 
For that purpose, STAT framework is enhanced with a dedicated mechanism. For each header-file it insures to include that instance, which appears first on the include-patch. The order is defined to the one the directories are mentioned for the given test-package. It works even if the header-file 
is included by other header files that are located in the same directory. It is achieved by symbol-linking or copying the header-files into a dedicated single directory.

### 2.3. CUT Isolation

#### 2.3.1. *Dependencies / DOCs*

One of the problems in unit-testing is resolving the dependencies of the given CUT. In embedded environment the problem gets even more complicated by the fact that the product is not pure software. However, the challenge is not only limited to HW-related issues.

Without substituting the DOCs with test-doubles, unit-testing might become a real nightmare in many aspects, e.g. complexity, timing, maintainability. Such tests would be very fragile and hardly scalable.

Another challenge is the amount of DOCs. One might say that with appropriate design really noticeable DOCs shall be few in number. While it's correct regarding the key DOCs, many times there are lots of insignificant dependencies, usually dispersed over many system components (e.g. logging, system calls).  

If the product architecture comprises more then on CPU, in embedded most likely it would be AMP architecture (Asymmetric Multiprocessing). It complicates things even more. If the product has OS, it also adds extra challenges to unit-testing.

#### 2.3.2. *'Noise' Dependencies*

Not all of the dependencies are equal from perspective of each given CUT: 

* There are key dependencies, which define the end-to-end use-cases/flows of CUT
* There are non-key dependencies, which do not define the major functionality of CUT
* There are also 'inconvenient' dependencies, which might serve as key dependency, but are hard to deal with
    * Usually, these are heavy-legacy components, e.g. overloaded with things like macros, strongly coupled APIs

The latter two types of DOC are usually responsible for fragile nature of unit-test packages, if not dealt with correctly.
We call these '***Noise***' dependencies.  
Let's see the following example of CUT relationships with its DOCs in a production code.  

![CUT Relationships](./media/cut_in_legacy.png)  

>On the figure above, one can see that the CUT has six DOCs: A,B and C are key dependencies and D, E, and F got identified as 'noise' dependencies. In C there are no built-in interfaces. Even header files (especially legacy) might contain partial implementation. In embedded environment, performance consideration might drive in favor of such decision (e.g. inline API functions). Therefore, the interfaces are denoted virtually on the figure (highlighted with dashed lines). 
 
#### 2.3.3. *'Noise' Reduction/Decoupling*

Decoupling a given CUT from its '*Noise*' DOCs improves its testability. The following figure shows how design-pattern '*Facade*' can be used to achieve this goal.

![CUT Relationships](./media/cut_isolation.png) 

We simply put a header files between CUT and all its '*Noise*' DOCs. Thus, it can be seen that CUT now depends only on four interfaces, rather then six.

>It's highly important to remember that such header serves as a wrapper and shall not contain functional logic. Abusing this technique will inevitably hurt the test-coverage.

By the way, '*Facade*' is not the only design-pattern suitable for the job:
* The '*Adapter*' design-pattern can be used to simplify or convert complicated DOC APIs.  
* The '*Strategy*' design-pattern can be used to resolve a use-case when different DOC APIs shall be called depending on strategy
  * For example, the strategy indication might appear in a form of enumeration. Thus, the implementation of the strategy would be a simple switch-case.
  
>For the sake of simplicity, these substitutions are denoted as '*Facade*' on all further figures.

## 3. Unit-testing Model

### 3.1. Test-Package Model

Now, when dependencies have been reduced to a reasonable minimum the test-package for the CUT would have the following view, which is much simpler than it would have been without those manipulations.

![CUT Relationships](./media/unit_test_package.png)  

>Please note that real DOC headers got replaced with dummy interfaces and DOCs with test-doubles.  
>Moreover, the test-package environment seems much simpler then it could have without '*Facade*'. 

### 3.2. Test-Doubles

There are several useful types of test-doubles:

* **Stub** is a most primitive form of test-doubles
    * It returns canned values (if any) with no regard to input
    * Usually are used to satisfy the compilation and as such serve almost no unit-testing purpose, except for passing our test-package through compilation
    * Many times this term is also used as a generic name for all types of test-doubles
* **Fake** test-doubles are a little bit more sophisticated than stubs and, thus, might be found useful for unit-testing in some specific cases.  
    * Such test-doubles generate valid fake outputs during the very test, usually based either on the input or some design-constraints, which usually make it impossible to pass a test without going through this API.
    * For instance, an API that returns a RAM buffer, without which our CUT-code cannot proceed any further.

Spies and Mocks represent a different, more superior league of test-doubles, as they provide a more effective set of controls for better unit-testing:

* **Spy** test doubles are the ones that are designed to collect and store aside the test-double inputs 
  * The inputs are supplied by our CUT during the test
  * The collected data can be validated after the CUT has been exercised
* **Mock** is the most sophisticated form of test-doubles. It is probably the most powerful test-double type:
    * Mocks are test-doubles that are programmed to provide specific output for a certain anticipated call in the test.
    * This type of test-doubles is almost irreplaceable in flow control, allowing the developer constructing any desirable flow at considerably low effort.

Needless to say that test-doubles usually do not fall into a definition of a single type, but rather come in a form of combination, like: 
* Spy with Mock   
    _or_ 
* Fake with Spy

### 3.3. Callbacks

Another technique quite useful with test-doubles is callbacks. Enhancing a test-double with ability to accept a callback gives the developer the ability to do some extra stuff, like emulating concurrency.

>*For instance*: let’s say our CUT is waiting in a loop for a certain global variable to change, while calling OS API that puts it to sleep in each cycle of the waiting loop.  
>In this example a callback, properly incorporated into the test-double of the corresponding OS API, can change the global variable to the desired state after a certain amount of calls. This gives the desired effect of asynchronous concurrent activity without actual concurrency.

### 3.4. Code-Sharing Model

Test-doubles in certain perspective represent a code-duplication. Therefore, we educate our developers to cooperate similar to open-source community. The effort of someone might provide solution to someone else, if properly exposed for sharing.

Therefore, we obligate our developers to consider each time they implement a test-double, whether it is worth-sharing with other developers. And if so, the developers are instructed to place such test-doubles into the dedicated focal directory, where other developers might find it and reuse in their test-packages.

## 4. Summary

The techniques '***CUT-Isolation***' and '***Dummy Interfaces***' have proved themselves throughout the years, during which we honed and polished this methodology.  
STAT-framework has evolved all along this entire process, deriving its design from the experience we gained. It is designed and built to ensure very simple and quick setup of unit-tests and to be very convenient for practicing TDD. And all this in conditions of heavy-legacy code-base and with minimal requirements (if any) for integration to the development environment.  
It helped us to establish the 'isles' of TDD in our code-base and to start gradual expansion of TDD over the rest of the code.
