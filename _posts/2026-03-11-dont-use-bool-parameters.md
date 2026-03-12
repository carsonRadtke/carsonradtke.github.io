---
layout: post
title: "Don't Pass bool Parameters in C++"
date: 2026-03-11
categories: c++
excerpt: "Raw bool flags make call sites opaque and error-prone. Strongly typed Yes/No enums keep intent explicit and let the compiler catch argument mix-ups."
---

In every codebase I've ever worked on, I have seen something that looks like:

```c++
    some_function(true, false, false, true, false);
```

That is unreadable, at least (sometimes) each argument is annotated with a comment:

```c++
    some_function(
        /*should_failfast=*/true,
        /*should_retry=*/false,
        /*skip_cleanup=*/false,
        /*telemetry_enabled=*/true,
        /*verbose_trace=*/false);
```

This is a bit better, at least for this call-site.
Comment-based annotations are difficult to enforce and you can always find cases where the annotation was missed.
Moreover, this is really easy to mess up.
What if a new option is added to the declaration, but a caller adds it in the wrong slot?
Now we have both a bad call-site and bad annotations.

It would be much better to have a call-site that is the best of both worlds:
1. Is self-documenting, so you don't need the comment.
2. Is strongly typed so you can't put an actual in the wrong slot.

Example of the goal:
```c++
    some_function(
        ShouldFailFast::Yes,
        ShouldRetry::No,
        SkipCleanup::No,
        TelemetryEnabled::Yes,
        VerboseTrace::No);
```

Looking at the call-site, it is obvious what each argument does.
Also, if you mis-ordered any of the arguments, you would get a compiler error.

Now, how could we go about implementing this?
First we need a concept that describes a YesNoEnum:

```c++
template <typename T>
concept YesNoEnum = requires {
    T::No;
    T::Yes;
} && sizeof(T) == 1 && T::No != T::Yes;
```

As per the concept, we have the following requirements:
- Both `No` and `Yes` are members of the `T` aggregate.
- `T` is a single byte in size.
- `T::No` is not the same as `T::Yes`.

And we can create a helper macro to help us define custom `YesNoEnum` types:

```c++
#define DEFINE_YNE(name)        \
    enum class name : bool {    \
        No = false,             \
        Yes = true,             \
    };                          \
    static_assert(YesNoEnum<name>)
```

Now we can declare our own fancy functions:

```c++
DEFINE_YNE(ShouldFailfast);
DEFINE_YNE(ShouldRetry);
DEFINE_YNE(SkipCleanup);
DEFINE_YNE(TelemetryEnabled);
DEFINE_YNE(VerboseTrace);

// ...

void some_function(ShouldFailfast, ShouldRetry, SkipCleanup, TelemtryEnabeld, VerboseTrace);
```

And we can call our fancy function:

```c++
    some_function(
        ShouldFailFast::Yes,
        ShouldRetry::No,
        SkipCleanup::No,
        TelemetryEnabled::Yes,
        VerboseTrace::No);
```

But how do we go about checking each argument?

Sure we could do:

```c++
    if (verbose_trace == VerboseTrace::Yes) { /* ... */ }
    if (should_fail_fast == ShouldFailFast::Yes) { /* ... */ }
    // ...
```

But that feels too verbose, what if we had some sort of helper?

```c++
template <YesNoEnum E>
[[nodiscard]] constexpr bool is_yes(E e) noexcept {
    return e == E::Yes;
}
```

Perfect! Now we have a clean way of checking our arguments:

```c++
    if (is_yes(verbose_trace) { /* ... */ }
    if (is_yes(should_fail_fast) { /* ... */ }
```

When joining new codebases, I often face resistance to this form of argument passing.
It is certainly less convenient and the DEFINE\_YNE certainly doesn't feel clean (it isn't).
But it helps prevent bugs and makes code maintenance easier.
It also helps your friendly neighborhood LLM to get a little more context when inspecting your code.

*AI Disclaimer: The article was written by a human (me); AI generated the title and summary.*
