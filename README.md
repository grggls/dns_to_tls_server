# Challenge:
A working example of a DNS to DNS-over-TLS proxy that can:
 1. Handle at least one DNS query, and give a result to the client.
 1. Work over TCP and talk to a DNS-over-TLS server that works over TCP (e.g: Cloudflare).

# Deliverables:
1. The source code.
1. A [Dockerfile](Dockerfile), and the different options required to run your software.
1. This README.md file

## Implementation Details:

## Choices:
We chose to use Python3 for this exercise because it is the language we're most comfortable with.

While we fully recognize the nature of the brief and the desire to have a DNS proxy listening on port 53, we chose a non-privileged port for the initial implementation, in order to simplify development and testing, without the need for privileged runtimes.

For the sake of brevity and extensibility, we excluded quite a bit of tooling necessary to make this service run well and remain supportable in a microservices environment: exporting metrics in a manner consumable by something like Prometheus, standard log formatting beyond what's needed to debug the service, the ability to talk with a SIEM service, etc. Perhaps in a full-bore microservice implementation, we'll be able to import a nice library to include these primitives in to our service almost as an afterthought.

## Follow-up Questions:
 ### *What are the security concerns for this kind of service?*

 This service aims to solve an extant security threat - namely that there is no sender-validation in the current (ancient) DNS spec. As such, DNS reflection attacks are prevalent and all systems which use traditional DNS can be MITM'd and leak information.

 Therefore it is essentially that this service minimize or completely solve for these concerns. As a TLS'd proxy connection, our service should not leak information or represent an attack surface for a MITM attack. Exceptions to this rule might be in cases where the endpoint (Cloudflare) CA has been compromised, or where our service has been made to ingest a compromised CA.

 Regarding general Docker security, we endeavored to decrease the blast radius of a compromised DNS-over-TLS proxy by attempting to run the daemon as a non-root user. We can further decrease the privilege of a running instance of this service by using a non-privileged port number (greater than 1024). Choosing 8053, for example, would require fewer privileges from the scheduling Docker daemon.

 ### *Considering a microservice architecture; how would you see this the dns to dns-over-tls proxy used?*

 In short, the Ambassador Pattern. This proxy could be well-used as sidecar container within a Kubernetes pod to compliment a main application container that makes outgoing DNS requests. With some simple port mapping, the main application would be made to proxy DNS queries via the sidecar container (our proxy) and have little knowledge of what is happening upstream.

 ### *What other improvements do you think would be interesting to add to the project?*

 We can offer a performance benefit with this service, along with the security benefits already outlined, by caching Cloudflare responses within the service for a configurable TTL and responding to new queries with those cached values. Performance benefits in saved network wait time would grow linearly with each DNS query that we were able to successfully serve from cache.
