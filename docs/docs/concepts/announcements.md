---
id: announcements
title: Announcements
sidebar_position: 4.5
---

# Announcements

An Announcement is a message the producing team posts on an **[Output Port](./output-ports)** to tell its consumers about an issue, a planned change or news. Announcements are listed on the Announcements tab of the Output Port, newest first.

## Posting and deleting

Anyone who may update the Output Port can post an Announcement and delete one. Deleting an Announcement also removes the notifications it sent.

Every Announcement has a title, a message, an optional link and one of five types:

| Type | Meaning |
| --- | --- |
| Issue | The data is wrong, late or missing right now. |
| Action needed | Consumers must change something: a deprecation, retirement or breaking change. |
| Planned maintenance | Temporary downtime or delay in a known window. |
| New version | Something improved. Nothing breaks on the consumer side. |
| Info | General news. |

## Reading

Anyone who can see the Output Port can read its Announcements. The Announcements of an Invite only Output Port stay hidden from everyone who cannot see that Output Port.

## Notifications

When an Announcement is posted, the portal notifies:

- the members of every Consuming Data Product, including members through a group;
- the owners of every Exploration that consumes the Output Port.

The producing team and the author are not notified.

Consumers see the Announcement in three places:

- the notification bell, which lists requests first and Announcements after them;
- a "new announcements" badge next to the Output Port on the Input Ports tab of the Consuming Data Product;
- the Notifications block at the top of the Home page. It shows up to five requests waiting for your decision, with a link to all of them in the Product Studio, and up to five Announcements, the most urgent type first (Issue, Action needed, Planned maintenance, New version, Info).

Acknowledging an Announcement in the bell or on the Home page removes its notification everywhere. The Announcement itself stays on the Output Port.
