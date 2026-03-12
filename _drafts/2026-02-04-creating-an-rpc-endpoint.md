---
layout: post
title: "Title Pending: Something about Coroutines and Threading"
date: 2026-02-04
categories: c++
excerpt: "TODO (@carsonradtke)"
---

Building a robust RPC system in modern C++.

## Overview of System:

### The Main (UI) Thread

There are many instances where (heavy) work should not be done on the main thread.
This is to ensure a smooth user experience.
For example, Android will trigger an ANR (Application Not Responding Error) when the UI thread is blocked for too long.
The idiomatic solution in this scenario is to move all work to a background task.
That's what this post is about.

### The Watchdog

In order to simulate Android's ANR, there is a thread constantly running that expects to receive periodic pings from the UI thread.
If the watchdog hasn't recieved a ping in a specifed timespan, it terminates the process.

### RPC Server

The RPC server listens for and schedules RPC requests.

### Worker

The worker thread takes scheduled RPC requests and executes them.

## Running Tasks on the Main Thread

Sometimes we _need_ to run a task on the UI thread.
Sticking with the Android analogy, you can access the Android UI toolkit exclusively from the main thread.
So there needs to be some mechanism for starting work on the worker thread and finishing it on the main thread.
