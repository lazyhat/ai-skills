# Architecture

`worker-a` is the sole owner of the durable queue. Consumers may read leases but must not create a second owner.
