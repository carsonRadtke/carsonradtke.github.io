---
layout: post
title: "Converting main() Arguments To Modern C++: Why Is It Harder Than It Should Be"
date: 2026-01-03
categories: c++
excerpt: "The C++ Core Guidelines recommend using std::span and std::string_view, but converting main()'s argv to follow these guidelines reveals a subtle ownership challenge and requires an unexpected detour through std::vector."
---

The entry point for C++ programs is `int main(int argc, const char* argv[])`.
What do the C++ Core Guidelines say about these formal parameters?

- [R.14: Avoid [] parameters, prefer `span`](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#r14-avoid--parameters-prefer-span).
- [SL.str.2: Use `std::string_view` or `gsl::span<char>` to refer to character sequences](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#slstr2-use-stdstring_view-or-gslspanchar-to-refer-to-character-sequences).

In accordance to the Guidelines, the program entry point should accept a `std::span<std::string_view>`.
Although the signature of `main` cannot be changed, there should be an easy way of doing the following:
```c++
auto run(std::span<std::string_view> args) -> int;

auto main(int argc, const char* argv[]) -> int {
    // magically define `args`...
    return run(args);
}
```
<details markdown="1">
<summary>Details</summary>
[❌ godbolt](https://godbolt.org/z/cnT3hn7EY)
```c++
#include <span>
#include <string_view>

auto run(std::span<std::string_view> args) -> int;

auto main(int argc, const char* argv[]) -> int {
    // magically define `args`...
    return run(args);
}
```
</details>
<br/>

The first thought is to just create the span directly:
```c++
auto main(int argc, const char* argv[]) -> int {
    return run(std::span<std::string_view>(argv, argc));
}
```
<details markdown="1">
<summary>Details</summary>
[❌ godbolt](https://godbolt.org/z/jn18c696P)
```c++
#include <span>
#include <string_view>

auto run(std::span<std::string_view> args);

auto main(int argc, const char* argv[]) -> int {
    return run(std::span<std::string_view>(argv, argc));
}
```
</details>
<br/>

And the compiler protests ([❌ godbolt](https://godbolt.org/z/jn18c696P)):
```
error: no matching constructor for initialization of 'std::span<std::string_view>' (aka 'span<basic_string_view<char>>')
    return run(std::span<std::string_view>(argv, argc));
```

The diagnostic output of the compiler is quite a bit more verbose, but here is the fundamental issue:
> A span is a view over a contiguous sequence of objects, the storage of which is owned by some other object.
- [span.overview-1](https://eel.is/c++draft/views.span#span.overview-1)

__Who is going to own each `std::string_view`?__

The owner of all the `std::string_views` needs to satisfy the following constraints:
 
1. It must offer a contiguous sequence of objects for which the `std::span` can "span" over.
2. It must own said contiguous sequence of objects.

These properties are more or less the traits required for the _ContiguousContainer_ named requirements.

Standard library types that satisfy these requirement include:

- `array`
- `basic_string`
- `inplace_vector`
- `vector`

`std::array` and `std::inplace_vector` are insufficient because there is a compile-time capacity associated with the type.
`std::basic_string` won't work because `argv` is not a character sequence; that leaves `std::vector`.

Here is the implementation with `std::vector`:
```c++
auto main(int argc, const char* argv[]) -> int {
   auto args = 
        std::span(argv, argc) |
        std::views::transform([](const char* arg) -> std::string_view { return { arg }; }) |
        std::ranges::to<std::vector<std::string_view>>();
  return run(args);
}
```
<details markdown="1">
<summary>Details</summary>
[✅ godbolt](https://godbolt.org/z/5Kbh7Gsdb)
```c++
#include <algorithm>
#include <range>
#include <span>
#include <string_view>
#include <vector>

auto run(std::span<std::string_view> args) -> int;

auto main(int argc, const char* argv[]) -> int {
   auto args = 
        std::span(argv, argc) |
        std::views::transform([](const char* arg) -> std::string_view { return { arg }; }) |
        std::ranges::to<std::vector<std::string_view>>();
  return run(args);
}
```
</details>

### Final Thoughts

Is allocating a container and populating it with `std::string_views` worth the trouble?
Surely it makes more sense to avoid the allocation and lazily build each `std::string_view`, right?

My personal projects allocate a container and `run` takes a `span` over a collection of `string_view`s because I like that style.
I also understand the philosophy of not doing unnecessary work.
At work, I would probably reach for a `std::span<const char*>` because it is easier and won't raise any eyebrows during code review.

It ultimately comes to a mixture of personal preference and context. 

---

<details markdown="1">
<summary>Bonus</summary>

An alternative owner type from the Guidelines Support Library (GSL): `gsl::dyn_array`<sup>1</sup> offers a container<sup>2</sup> whose size is fixed, but not known until runtime.
It can be thought of as a `std::vector` without the methods necessary for resizing (and is thus a smaller type).

```patch
-        std::ranges::to<std::vector<std::string_view>>();
+        std::ranges::to<gsl::dyn_array<std::string_view>>();
```

> <sup>1</sup> `gsl::dyn_array` was recently added to the Guidelines.
It will soon be implemented in [Microsoft/GSL](https://github.com/Microsoft/GSL).

> <sup>2</sup> `gsl::dyn_array` is not a "container" in the named requirements sense of the word.
It is not movable so it's iterators can never be invalidated.
</details>
<br/>

*AI Disclaimer: The article was written by a human (me); AI generated the title and summary.*
