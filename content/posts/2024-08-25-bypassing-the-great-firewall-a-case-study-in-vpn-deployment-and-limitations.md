---
title: 'Bypassing the Great Firewall: A Case Study in VPN Deployment and Limitations'
date: '2024-08-25T21:10:16-07:00'
slug: bypassing-the-great-firewall-a-case-study-in-vpn-deployment-and-limitations
aliases:
- /2024/08/25/bypassing-the-great-firewall-a-case-study-in-vpn-deployment-and-limitations/
categories:
- Occupation | 营营
tags: []
lang: en
draft: false
comments: true
wp_id: 1587
---

China’s Great Firewall (GFW) is a formidable barrier, effectively restricting domestic access to external internet resources. While the broader implications of this censorship are beyond the scope of this post, I want to share a recent experiment that highlights some challenges in circumventing it.

The premise was straightforward: deploy a VPN server on an EC2 instance with a public IP address, and use that IP address within China to bypass the GFW. To expedite the process, I utilized a well-regarded repository for setting up an IPsec VPN: [GitHub – hwdsl2/setup-ipsec-vpn](https://github.com/hwdsl2/setup-ipsec-vpn/tree/master). Using their CloudFormation template, I launched a `t2.micro` instance in the `ap-southeast-1` region. The deployment was seamless, and the output included a `.mobileconfig` file, easily importable into MacOS for VPN configuration.

However, after establishing the VPN connection, I noticed significant latency issues. Web pages were extremely slow to load, and ICMP tests revealed frequent timeouts.

Upon investigation, I found that AWS provides no network performance guarantees for `t2.micro` instances, which likely contributed to the poor performance. Upgrading to a t3.micro instance, which includes a minimum of 5 Gbps of bandwidth, resolved the issue, allowing smooth access to Facebook, which is otherwise blocked in China.

Next, I attempted to configure a VPN client, StrongSwan, as recommended by the repository. The AWS StackSet output provided a `.sswan` configuration file, but transferring this file via WeChat proved problematic. The file was consistently blocked during transmission, leading me to suspect that WeChat’s file filtering might be based on file extensions. Renaming the file to something less conspicuous (e.g., something.s1swan) didn’t resolve the issue until I rebooted WeChat, indicating that file filtering might also be session-based. FTP file servers could have been another solution but would require more setup.

Despite initial success, the VPN connection was disrupted after just two minutes and remained unusable for the next 24 hours. I suspect that the GFW detected and recorded the public IP address of my VPN server, leading to its subsequent blocking.

While it’s possible to circumvent this by rotating a pool of public IP addresses, I haven’t found an off-the-shelf solution that provides a user-friendly interface for non-technical users. Additionally, maintaining such a pool for personal use presents economic challenges.

Overall this quest hasn’t been successful, but may highlight some blockers in case you are considering the same.
