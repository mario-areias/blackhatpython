# Chapter 2: The Basics

## Scripts

### TCP Server and Client 

Those are the scripts `tcp_client.py` and `tcp_server.py`. They are very small scripts and are not very useful. Only foundational blocks for more advanced scripts.

#### Changes from the book

No changes

### Netcat

This is the script `netcat.py`. A very interesting script trying to replicate all original netcat functions.

#### Changes from the book

I have added support for two different commands: 

`exit`: When running in iterative mode, the `exit` command will kill the client, but not the server.

`exit_server`: When running in iterative mode, the `exit_server` command will kill the server and the client. Be careful with this one.

Fixed a small bug related to a race condition, when returning the output of a command followed by the banner, the client would sometimes be in a weird state. By sending together, this has does not happen anymore.

### TCP Proxy

This is the script `tcp_proxy.py`. It is a very simple TCP proxy, that proxies connections to a specific server.

#### Changes from the book

The original script only supported http connections. I've added support to have, on the remote end, https connection. So while the proxy receives http requests, it can send https requests to the remote.

### Netcat SSH commands

These are the scripts `nc_sshcmd.py`,  `nc_sshRcmd.py` and `nc_sshServer.py`. They are a suite of program to replicate a few of SSH functions.

#### Changes from the book

Nothing much apart from add support to connection to a SSH port different from 22. As well as receive parameters on the script, rather than hardcode them.

### SSH tunelling

Paramiko provides an useful example with the [rforward.py](https://github.com/paramiko/paramiko/blob/master/demos/rforward.py) file.