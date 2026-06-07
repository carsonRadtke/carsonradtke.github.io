---
layout: post
title: "Many arguments is better than a large struct"
date: 2026-03-11
categories: c++
excerpt: "TODO (@carsonradtke)
---

TODO: Discuss how swapping `foo(int a, int b, int c)` for `foo(struct foo_args { int a, int b, int c})` is not an improvement.
It leads to partially initialized values. 
