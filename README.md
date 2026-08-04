# Local AI

A personal knowledge base and infrastructure repository for running Large Language Models (LLMs) locally.
Rather than focusing on model development, the goal is to explore the deployment and operation of open-source AI systems on Linux.

## Focus Areas

* Linux system administration
* Self-hosted AI
* Local LLM deployment
* Containerized infrastructure
* GPU acceleration
* AI tooling and workflows
* Documentation and knowledge management

## Technology Stack

* Linux
* Docker / Docker Compose
* Open WebUI
* LiteLLM
* Ollama
* vLLM
* Python
* Bash

### resources.txt

One of the main goals of this repository is maintaining a curated collection of useful resources, including:

* official documentation
* model repositories
* deployment guides
* useful tools and utilities

Instead of searching the web every time, this file acts as a growing reference for technologies related to local AI.

## Current Architecture
                Open WebUI
                     │
                     ▼
                 LiteLLM
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
      Ollama                  vLLM
      

The architecture is intentionally modular, allowing inference backends to be exchanged or expanded without changing the frontend.

## Goals

This repository is intended to evolve over time.
Planned topics include:

* deployment automation
* monitoring
* authentication
* reverse proxy integration
* GPU optimization
* AMD ROCm
* NVIDIA CUDA
* multi-GPU deployments
* benchmarking
* infrastructure documentation

## Purpose

This project is primarily a personal learning and documentation repository.
It allows me to collect knowledge, experiment with different deployment strategies and continuously improve my understanding of Linux-based AI infrastructure.
No proprietary code from my employer is included.
Some of these softwares were alredy tested on local hardware in one of my past positions.
