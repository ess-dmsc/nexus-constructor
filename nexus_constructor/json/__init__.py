"""
Package for loading and creating json representations of an InstrumentModel that can be used by the ESS DMSC's nexus
filewriter https://github.com/ess-dmsc/kafka-to-nexus/

Note that due to format differences, saving and re-loading nexus json isn't entirely lossless.
Conversion can introduce floating point errors into cylindrical geometry and transform axes, and components without an
explicitly defined dependent transform in their transform parent will have one assigned when saving.
"""
