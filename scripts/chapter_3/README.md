# Chapter 2: Raw sockets and sniffing

## Scripts

### Sniffer with ICMP

This is the script `scanner.py`. It is a very simple host discovery scanner

#### Changes from the book

As suggested by [this post](https://stackoverflow.com/a/29307402) I've changed the fields `src` and `dst` to be `c_uint32` rather than `c_ulong`. I also changed the struck pack parameter from `<L` to `@I`. Finally, changed the code instead to get the first 20 bytes for the IP header, to send all of them.

Also, I've added arguments for host and subnet (rather than leave hardxcoded), as well as, options to save to a file, change the magic message and more.
