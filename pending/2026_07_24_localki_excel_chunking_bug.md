---
title: "Why a tax advisor's Excel habit broke my RAG pipeline"
date: 2026-07-24
project: LocalKI
status: tested
stack: FastAPI, ChromaDB, BM25 hybrid retrieval, Ollama Qwen 2.5 14B, Electron and React frontend
hardware: PC1, fully offline
---

**TESTED** · LocalKI pilot session · offline RAG stack, PC1

LocalKI is the RAG workstation I've been building for German tax advisors, running fully offline, no cloud calls, everything local on PC1. It's near pilot ready. My pilot user, Anna, has been putting it through real client files, and real client files break things in ways clean test data never does.

Six bugs came out of her last pilot session, tracked as BUG_F01 through BUG_F06. Most of them were the usual pilot noise. One wasn't.

Anna converts every Excel file to PDF before she uploads it. Not a workaround, just her normal habit from years of working the way tax software expects. It turns out that single habit was the root cause of most of the chunking failures the pipeline was throwing. A spreadsheet has structure, rows, columns, a Mandant's numbers sitting in a specific relationship to each other. Flatten that into a PDF first, and the structure that the Structure Registry depends on, the 44 label canonical taxonomy that classifies incoming documents, has already been lost before the system ever sees the file.

The fix isn't "tell Anna to stop doing that." Real tax advisors are not going to change a habit that predates the software by a decade. The fix is Excel native ingestion, reading the spreadsheet directly instead of asking the pipeline to reconstruct structure from a PDF that already threw it away.

[Placeholder: exact chunking accuracy before and after the fix, once the Excel native path is benchmarked against the SteuerEx set]

Why this matters past LocalKI specifically: if you're building any local AI system that ingests documents from real users instead of test fixtures, watch what format they hand you before you optimize your chunking logic. The bug usually isn't in the chunker.

Next entry: how the correction and learning memory layer is handling Anna's fixes so the same mistake doesn't get made twice.
