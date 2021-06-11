# Network Protocol Differential Testing

In this repository, a software framework is proposed and implemented which follows the approach of differential testing. Its focus lies on performing test suites on network protocols. In a first step, a communication sequence between a test agent and a reference platform (Golden Platform) is recorded. This step is repeated with the same test agent but a platform under test as the target platform. Finally, the two recorded sequences are compared and unexpected differences are reported.

The network protocols and their associated protocol fields, that have to be taken into account during the network packet comparison, are configurable arbitrarily. Further on, the differential testing framework offers a mechanism to check for timing violations between single data packets within a network communication sequence.
