---
id: announcements
title: Announcements
sidebar_position: 4.5
---

# Announcements

An Announcement is a message the producing team posts on an **[Output Port](./output-ports)** to tell its consumers about an issue, a planned change or news. Announcements are listed on the Announcements tab of the Output Port, newest first. Anyone who sees the tab can search the Announcements by title and message.

## Posting and deleting

Anyone who may update the Output Port can post an Announcement and delete one. Deleting an Announcement also removes the notifications it sent.

Every Announcement has a title, a plain-text message and one of three types, shown as a coloured icon before the title:

| Type | Meaning |
| --- | --- |
| Action needed | Consumers must change something: a deprecation, retirement or breaking change. |
| Warning | Something is wrong or will be: late or incomplete data, an incident or planned maintenance. |
| Info | News that needs no action, such as a new version. |

Links in the message that start with `http://` or `https://` become clickable. Long messages are cut off after three lines with a "more" link.

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
- the top of the Home page. It shows up to five requests waiting for your decision, with their total count and a link to all of them in the Product Studio, and up to five Announcements, the most urgent type first (Action needed, Warning, Info). "Read more" on an Announcement shows its full message and its Output Port. Sections without items are hidden.

Acknowledging an Announcement in the bell or on the Home page removes its notification everywhere. The Announcement itself stays on the Output Port.

## Future versions

Announcements belong to a single Output Port. Announcements on a whole Data Product, for news that concerns all its Output Ports, are planned for a later version.
