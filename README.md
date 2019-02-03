# Challenge:
A working example of a DNS to DNS-over-TLS proxy that can:
 1. Handle at least one DNS query, and give a result to the client.
 1. Work over TCP and talk to a DNS-over-TLS server that works over TCP (e.g: Cloudflare).

# Deliverables:
1. The source code.
1. A [Dockerfile](Dockerfile), and the different options required to run your software.
1. This README.md file

## Implementation Details:
We like to start a software project with a couple of niceties:
 - a Makefile to make code->run->validate loops as easy as possible
 - a target in that Makefile to quickly drop us into an interactive shell on the container where we're working
 - another target in that Makefile that makes working with a local docker repo fast and painless
 - some semblance of how our code will be packaged and run in production (docker here, thankfully) and its mirror in this code->run->validate loop. Here that was as easy as a Dockerfile and a requirements.txt file called from within it. In more complicated projects that might involve running artifactory and jenkins locally, so that we know our code will play nice when it's finally integrated. (That's way too complicated a path to production for my liking. Complicated development environments are a code smell.)

I don't have a huge amount of experience with wire protocols to be honest. The last time I had to think about composing datagrams, I was at university. I took the first step of making this work with a piece of already written [software](https://github.com/curl/doh). Once I had my project working and testing in a comfortable way, and had a sense of what a DNS over HTTPS resolver traffic looks like, what kinds of validation and sanitization the inputs and outputs might need, I moved on to implementing my own DNS over TLSresolver.

As regards error checking and client experience, we expect that it will be machines, not humans, making the most of this service. Since we've all seen machines misbehave, and because we have no details about the microservice environment, API gateways, or if there's any backpressure implemented in this system, we chose to implement our server in a somewhat defensive way: client connections that send valid DNS queries will be maintained and a (within reason) unlimited number of requests can be made on the same reused connection. Invalid DNS queries, non-utf-8 characters, and any type of unvalidatedable input will result in the connection being closed, at which point the client of this service will need to reconnect.

## Choices:
We chose to use Python3 for this exercise because it is the language we're most comfortable with.

While we fully recognize the nature of the brief and the desire to have a DNS proxy listening on port 53, we chose a non-privileged port for the initial implementation, in order to simplify development and testing, without the need for privileged runtimes.

For the sake of brevity and extensibility, we excluded quite a bit of tooling necessary to make this service run well and remain supportable in a microservices environment: exporting metrics in a manner consumable by something like Prometheus, standard log formatting beyond what's needed to debug the service, the ability to talk with a SIEM service, etc. Perhaps in a full-bore microservice implementation, we'll be able to import a nice library to include these primitives in to our service almost as an afterthought.

## Follow-up Questions:
 ### *What are the security concerns for this kind of service?*

 This service aims to solve an extant security threat - namely that there is no sender-validation in the current (ancient) DNS spec. As such, DNS reflection attacks are prevalent and all systems which use traditional DNS can be MITM'd and leak information.

 Therefore it is essentially that this service minimize or completely solve for these concerns. As a TLS'd proxy connection, our service should not leak information or represent an attack surface for a MITM attack. Exceptions to this rule might be in cases where the endpoint (Cloudflare) CA has been compromised, or where our service has been made to ingest a compromised CA.

 Regarding general Docker security, we endeavored to decrease the blast radius of a compromised DNS-over-TLS proxy by attempting to run the daemon as a non-root user. We can further decrease the privilege of a running instance of this service by using a non-privileged port number (greater than 1024). Choosing 8053, for example, would require fewer privileges from the scheduling Docker daemon.

 Misbehaving or adversarial clients of this service will see their connection reset immediately. There are some edge cases I noticed during implementation that aren't handled here, specifically with non-blocking I/O. Better error handling, tracking of misbehaving client IPs, and flushing of the socket would all make this a sturdier service in production.

 ### *Considering a microservice architecture; how would you see this the dns to dns-over-tls proxy used?*

 In short, the Ambassador Pattern. This proxy could be well-used as sidecar container within a Kubernetes pod to compliment a main application container that makes outgoing DNS requests. With some simple port mapping, the main application would be made to proxy DNS queries via the sidecar container (our proxy) and have little knowledge of what is happening upstream.

 ### *What other improvements do you think would be interesting to add to the project?*

 We can offer a performance benefit with this service, along with the security benefits already outlined, by caching Cloudflare responses within the service for a configurable TTL and responding to new queries with those cached values. Performance benefits in saved network wait time would grow linearly with each DNS query that we were able to successfully serve from cache.

 As we have implemented it, the proxy can make use of a number of stub resolvers. It might be interesting to add a profiler to this proxy in a later version, in order to make some qualitative determination about the most performant implementation.
