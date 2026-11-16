---
id: announcements
title: Announcements
sidebar_position: 1
---

# Announcements

An Announcement is a message the producing team posts on an **[Output Port](./output-ports.md)** to tell its consumers about an issue, a planned change or news. Announcements are listed on the Announcements tab of the Output Port, newest first. Anyone who sees the tab can search the Announcements by title and message.

## Posting and deleting

Anyone who may update the Output Port can post an Announcement and delete one. Deleting an Announcement also removes the notifications it sent.

Every Announcement has a title, a plain-text message and one of three types, shown as a coloured icon before the title:

| Type | Meaning |
| --- | --- |
| Action needed | Consumers must change something: a deprecation, retirement or breaking change. |
| Warning | Something is wrong or will be: late or incomplete data, an incident or planned maintenance. |
| Info | News that needs no action, such as a new version. |

Links in the message that start with `http://` or `https://` become clickable.

## Reading

Anyone who can see the Output Port can read its Announcements. The Announcements of an Invite only Output Port stay hidden from everyone who cannot see that Output Port.

## Notifications

When an Announcement is posted, the portal notifies:

- the members of every Consuming Data Product, including members through a group;
- the owners of every Exploration that consumes the Output Port.

The producing team and the author are not notified.

Consumers can see the Announcement in three places:

- the notification bell, which lists requests first and Announcements after them;
- a "new announcements" badge next to the Output Port on the Input Ports tab of the Consuming Data Product;
- the top of the Home page. It shows the requests waiting for your decision, with a link to them in the Product Studio, and your new Announcements, the most urgent type first (Action needed, Warning, Info). Each card shows its count and scrolls when the list is long. "Read more" on an Announcement shows its full message and its Output Port. Sections without items are hidden.

Acknowledging an Announcement in the bell or on the Home page removes its notification everywhere. The Announcement can still be found on the Output Port.
