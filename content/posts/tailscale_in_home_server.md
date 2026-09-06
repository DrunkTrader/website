+++
title = "SSHing Into My Home Server, From Anywhere"
date = 2026-09-06
type = "post"
description = "How I use Tailscale and SSH to access my headless home server without exposing SSH to the public internet"
in_search_index = true
generate_feeds = true
[taxonomies]
tags = ["Linux", "Networking", "Devops", "Tailscale", "SSH"]
[extras]
og_preview_img = "/images/og/p1_tailscale_img.png"
+++

I have a headless server sitting at home.

No monitor. No keyboard. No particular interest in giving it either.

The problem with a headless server is fairly obvious: eventually, you need to talk to it.

I wanted to SSH into it from my laptop when I was away from home. The traditional solution would be to expose port `22` on my router and forward it to the server.

That works.

It also means putting an SSH service on the public internet and then spending the rest of your life making sure nobody interesting finds it.

There was a simpler solution.

[Tailscale](https://tailscale.com/) creates a private WireGuard-based network between my devices. My laptop and home server can talk to each other as if they were sitting on the same network, even when they aren't.

So I installed Tailscale on both.

On the home server:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

And the same on my laptop.

Once authenticated, the server showed up with its Tailscale IP:

```text
100.99.XX.XX
```

That's the important part.

I don't need to know my home router's public IP. I don't need to configure port forwarding. I don't need to expose SSH to the internet.

I just SSH into the Tailscale address:

```bash
ssh drunktrader@100.99.XX.XX
```

And I'm in.

The nice thing about this setup is that SSH itself doesn't really know—or care—that Tailscale is involved.

From SSH's perspective, this is just another IP address.

```bash
$ ip addr show tailscale0

...

inet 100.99.XX.XX/32 scope global tailscale0
```
![LogChef skill in action](/images/og/p1_tailscale_img.png)

Tailscale provides the network.

SSH provides the conversation.

Linux does the rest.

### The headless part

This becomes particularly useful when the server is doing something I don't want to interrupt.

I can connect remotely:

```bash
ssh drunktrader@100.99.XX.XX
```

check what's running:

```bash
systemctl --type=service --state=running
```

inspect processes:

```bash
htop
```

or just move files around with `scp`:

```bash
scp ./file.txt drunktrader@100.99.XX.XX:/home/drunktrader/
```

For larger files, the same idea applies.

At one point I needed to access a media file sitting on the server. Instead of turning the server into a public file server, I could simply use the existing Tailscale connection.

That's the pattern I keep coming back to:

**If the machine is already on my private network, why make the service public?**

### Tailscale SSH

Tailscale can also handle SSH itself, which removes some of the traditional SSH configuration.

For example:

```bash
tailscale up --ssh
```

This allows Tailscale to provide SSH access between devices in the tailnet.

But for my setup, regular OpenSSH over the Tailscale interface is perfectly sufficient.

I still get the familiar workflow:

```bash
ssh user@100.x.x.x
```

The difference is where that packet goes.

It stays inside the Tailscale network rather than asking my home router to expose port `22` to everyone.

### Finding the server

When I forget the Tailscale IP, I don't need to guess.

```bash
tailscale status
```

gives me the devices connected to my tailnet:

```text
100.xx.xx.xx   laptop        ...
100.99.XX.XX   home-server   linux
```

I can then connect directly:

```bash
ssh drunktrader@100.99.XX.XX
```

Nothing particularly clever is happening here.

That's the point.

### A small mental model

The setup is basically:

```text
                 Tailscale
        ┌─────────────────────────┐
        │                         │
        │                         │
    Laptop                    Home Server
   100.x.x.x                  100.99.XX.XX
        │                         │
        └────────── SSH ──────────┘
```

The server doesn't need a public SSH endpoint.

Both machines only need to be reachable through the same tailnet.

And because Tailscale handles NAT traversal and encrypted connectivity, the annoying networking details mostly disappear from the workflow.

The result is pleasantly uneventful.

I'm somewhere else.

I open a terminal.

```bash
ssh drunktrader@100.99.XX.XX
```

And my home server is there.

No port forwarding.

No public SSH port.

No hunting for the home IP.

Just SSH.

Fin.
