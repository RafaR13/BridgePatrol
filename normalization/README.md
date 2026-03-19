# Normalization Layer

In this layer, one gathers information from XChainDataGen's database, and maps bridges' specific events into a normalized version, for later analysis

## Structure
### common/
Common scripts and utilities
### mappers/
Mapping: bridge table --> normalized event
### runner/
Scripts to run the normalization process
### source_models/
Models for XChainDataGen repositories