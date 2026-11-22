---
title: 'ProdSec Interview Prep Guideline: Code Review'
date: '2024-08-30T08:35:00-07:00'
slug: prodsec-interview-prep-guideline-code-review
aliases:
- /2024/08/30/prodsec-interview-prep-guideline-code-review/
categories:
- Occupation | 营营
tags: []
lang: en
draft: false
comments: true
wp_id: 1600
---

This type of interview is intended to test your code review skill. You will be presented with a piece of codes, review them, identify security vulnerabilities, and suggest fixes. Evaluation usually happen on 4 aspects:

1. Code Navigation:
   1. speed: can you read codes in reasonable speed
   2. understanding: can you explain what those codes do
   3. methodology/habits: do you have a finely tuned method for code review
2. Bug Identification:
   1. comprehensiveness: can you identify most, if not all, security vulnerabilities
   2. exploitation: can you explain how those bugs can be exploited
3. Fix suggestion:
   1. resourcefulness: can you suggest bug fixes, sometimes in more than one way
   2. automation: can you suggest how those bugs can be auto detected and/or prevented
4. Communication
   1. explanation: can you explain all those to a developer who has little security experience

Those 4 aspects tend to have the same weight, although the hiring manager may also have their own heuristics for different levels. Here’s an example heuristic I’ve used before:

- Junior: identify 60% bugs, explain those bugs clearly to developers, suggest direct fixes
- Senior: identify 80% bugs, explain those bugs and preferably know how they can be exploited, suggest automated detection
- Staff: identify all bugs, use past experience to explain why they could be bad, suggested framework-level changes to prevent bugs from happening
- Senior Staff and above: all of the above, suggest multiple fixes/prevention/detection methods and compare pros and cons, demonstrate empathy towards developers

There is a limit to how this interview can go, because I wouldn’t expect a qualified senior staff prodsec engineer (Meta IC6) to differ much from a qualified principal or above(Meta IC7+) engineer in their code review interview performance. This differentiation among very senior levels comes mainly in other interviews.

To better illustrate my point, I’ll use a code snippet to demonstrate how a candidate can be evaluated.

---

*Interviewer:* In this interview, you are presented a code snippet. The code snippet may or may not contain security vulnerabilities. I’ll give you some time to review it first. You will then tell me what those codes do, how they are bad, and how they can be fixed. Cool?

*Candidate:* let’s do it!

*Interviewer*: display the following piece of code.

(Note: I prefer to show this piece of codes in highlighted PDF or on printed paper, instead of allowing candidate to view it in IDE. This gives me more insights into candidates’ **raw** review capability.)

Codes are here: <https://github.com/badass-aoz/security-interview/blob/main/prodsec/native_code_review.cpp>

Code Navigation:

The code snippet demonstrate a (shitty) CLI software that does reservation. It first authenticates users via username-password credentials, and then offered three options to create new reservation, change reservation, or view reservation.

The code snippet is relatively simple. A candidate may work their way top-down (from `main` function to aux functions, skipping functions in callers and looping back to them in callees) or bottom-up (DFS style, from `main` to aux functions then back to `main`). Either way is fine as long as candidate is methodical and demonstrates proficiency.

Bug Identification & Fix Suggestion:

1. Password stored in plaintext in DB: This is insecure because a compromised database (for example, insider threat) will mean compromised user login credentials.
   1. best practice: salt and hash the password; store password in a separate database from the product database, and store the salt along with the hashed password
   2. interviewer can choose to dig deeper:
      1. hashing related:
         1. what hashing algorithm would you recommend? bcrypt, scrypt, PBKDF2, etc.
         2. what makes a good password hashing algorithm and why? slow (*work factor*), cryptographically secure, low collision, etc.
         3. why is SHA256 bad? not secure, fast, collision, etc.
         4. why salt? rainbow table attack
      2. prevention:
         1. linter on password usage: for example, annotate all the APIs that handle passwords and create an alert that uses password, and have a devsecop pipeline to review usages
         2. introduce password policies (e.g. minimum password length + complexity), or even better, don’t use password (e.g. SSO).
2. Hardcoded secrets: `R00tP@ssw0rd` isn’t complex enough. Also don’t store this in plaintext in the code. Secrets in codes will leak.
   1. fix: remove it and load it from a secure place; or better, use an IAM solution with properly scoped role (e.g. a service account with privilege of only changing records to the relevant tables)
3. `strcmp` for password comparison: The function does character by character comparison, and returns early when it detects difference. This makes timing attack possible.
   1. fix: use constant time operation. You can either implement your own (by always iterating through all characters) or use an existing one (e.g. libsodium `sodium_memcmp` , OpenSSL `CRYPTO_memcmp` etc.)
4. SQL Injection: the code directly inserts user input into SQL statements without proper sanitization or using appropriate APIs.
   1. exploit: *Interviewer:* give me an example payload to exploit the SQL injection issue
      1. example: take this particular SQL as an example:
      2. `SELECT password FROM users WHERE username = \\"%s\\";`. We can make the username as `1" OR true; DROP TABLE users; --` This is not particularly useful or sneaky (just dropping table, no information leakage) but gets the work done.
      3. fix: user input sanitization can be useful if you know what to expect for a particular SQL statement. For example, if the SQL only expects an integer as input, then you can easily sanitize it. However, sanitization is generally error-prone and not recommended as the sole defense. Just use prepared statement or parameterized query.
      4. prevention:
         1. create a linter to detect insecure usages of SQL statement;
         2. alert on production SQL statement syntax errors. The idea is that in order to exploit a SQLi the attacker will usually need to try several times to get a working payload.
         3. a strong candidate may also mention creating a secure library that make it super easy to write codes securely, and making the friction of writing buggy codes extremely high
5. Insecure `sprintf` : `sprintf` doesn’t know about the destination buffer size limit. As a result, it can overflow the destination buffer is supplied a char string larger than the destination buffer.
   1. fix: use `snprintf` : it takes an additional argument for the size of the buffer and limits how much content can be stored in the buffer.
   2. followup: a candidate may also point out that the snippet is mixing modern C++ style with traditional C style coding (e.g. `char*` v. `std::string`). That’s correct and considered a bonus point.
6. Insecure buffer overflow check: closely correlated to above, the integer addition and comparison pattern is a classic recipe for integer overflow and subsequently bypassing buffer overflow check.
   1. followup:
      1. the interviewer can ask to implement a more secure boundary check (or integer addition with embedded
      overflow checks ([example](https://pastebin.com/LWkQRiTu))
   2. the interviewer may also ask about integer promotion
   3. prevention & detection:
      1. sanitizers: UBSan has integer overflow related flags `signed-integer-overflow` and `unsigned-integer-overflow` that can detect potential overflows, but they can easily get noisy
      2. safe libraries: build a set of libraries (for example, [SafeInt](https://github.com/dcleblanc/SafeInt) by my colleague LeBlanc) for common pitfalls such as integer overflow and recommend/enforce the usage of those libraries
7. Unbroken `case` statement: C/C++ doesn’t stop the execution of `case` unless it sees a `break` statement.
   1. fix: add a `break` statement.
   2. followup:
      1. prevent this with a linter
      2. if you are using gcc/clang, turn on `-Wimplicit-fallthrough` flag
8. Not checking return value for errors: for example, `changeReservation` caller should check the return value and error out in case of error.
   1. fix: check the return value
   2. followup:
      1. rely on C/C++ gcc/clang compiler’s `-Wunused-result` flag (along with **`[[nodiscard]]`** attribute).
      2. linter, as good as always
9. Double Free: note that the `session` object can be freed twice (heck, many more times) if you use a choice other than 1, 2 or 3. Double free is undefined and can potentially be used for heap-based buffer overflow.
   1. fix: remove the first `free` ; `null` ify the pointer free `delete`
   2. prevention and detection:
      1. use smart pointers consistently (e.g. `unique_ptr` in this case)
      2. Use ASan in your testing/canary CI pipeline
      3. static analysis is always a good bet
10. Mismatch between `new[]` and `free`: `delete[]` should be used instead of `free`. The main difference is around allocating raw memory v. additionally calling constructors/destructors. Mismatch memory (de)allocation can lead to memory corruption (e.g. an object getting `free` d but it could be managing other objects and those objects not getting properly destructed).
11. Memory leakage: the `welcomeMessage` is not freed at the end. This is probably fine given the size of the memory buffer and that the OS will eventually collect the memory after `main()` exits.
    1. followup: candidate may suggest using tools such as Valgrind or LeakSanitizer as part of ASan. As an interviewer I’d consider this relatively minor if candidate doesn’t mention this.
12. Leaking stack trace in `stderr`: it’s generally a bad idea to leak stack trace in program output directly to users. It’s more so in a webapp than here, because here the attacker has your binary anyway, whereas in a webapp usually the attacker has no access to the server binary. That said, why handling the attacker extra information when you can help?
    1. followup: taint analysis can be used to detect this type of issue
13. handling of secret in memory: after a successful login, when the program exits, `this->password` is most likely still in memory without be cleared up. This is risky because other programs may try to abuse this by reading into this particular memory.
    1. fix: zero out the `password` variable in destructor, for example by using `std::string::clear()` . Alternatively, just don’t store the password as part of the class in the first place.
    2. prevention: adding a secure framework class which acts as a wrapper for `string` -like secrets and automatically wipes memory in the destructor. There are some handy solutions out there such as ones provided by [libsodium](https://libsodium.gitbook.io/doc/memory_management#guarded-heap-allocations).

Phew. This is obviously not a comprehensive list of what you may encounter, and there can be more classic ones such as “return-after-free” and “use-after-free” bugs, but hopefully the above analysis gave you a good overview.

Communication:

Even though communication is a separate axis of assessment from the technical ones above, compared to other types of interview (in particular, behavior interview), communication performance is more closely correlated to technical ones. In other words, I haven’t seen a case when a candidate performed well in communication without performing at least equally well in technical axes.

It’s rare, but one trap that I have observed in weak candidates was that they’d straightly dive into a concept without explaining why. For example, they might be immediately diving into heap grooming (exploitation technique) without even explaining how the heap overflow was bad (vulnerability impact). Personally I’d cut enough slack for strong technical candidates if they are just too passionate with exploitation to bother with explaining the “obvious” thoroughly, but I’d recommend be considerate of where the interviewer wants you to hit.

Another trap I have observed is that candidates throw out some buzzwords and then fail to meaningfully follow up. For example, a candidate could mention *EternalBlue* or *Shellshock*.

“Great! How do they work?”

Total blank out.

And that doesn’t look good.

When you say something, make sure you can withstand the interviewer probing 3 layers deep. That’s what I always do when the candidate mentions something fashionable. It’s all fair game to me if it’s the candidate who raised a point.
