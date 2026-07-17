<!-- SupyGames: This plugin provides some fun games like (Russian) roulette, 8ball and monologue -->

Documentation for the SupyGames plugin for Supybot
==============================================

Purpose
-------

This plugin provides some fun games like (Russian) roulette, 8ball, monologue
which tells you how many lines you have spoken without anyone interrupting
you, coin and dice.

Install
-------

Limnoria ships its own built-in ``Games`` plugin, which also provides a
``monologue`` command. That built-in plugin **must be unloaded first**
(e.g. ``unload Games``) before loading SupyGames, otherwise the two
plugins will conflict over the same commands.

Usage
-----

This plugin provides some small games like (Russian) roulette,
eightball, monologue, coin and dice.

.. _commands-SupyGames:

Commands
--------

.. _command-supygames-coin:

``coin takes no arguments``
  Flips a coin and returns the result.

.. _command-supygames-dice:

``dice <dice>d<sides>``
  Rolls a die with <sides> number of sides <dice> times. For example, 2d6 will roll 2 six-sided dice; 10d10 will roll 10 ten-sided dice.

.. _command-supygames-eightball:

``eightball [<question>]``
  Ask a question and the answer shall be provided.

.. _command-supygames-monologue:

``monologue [<channel>] [<nick>]``
  Returns the number of consecutive lines you've sent in <channel> without being interrupted by someone else (i.e. how long your current 'monologue' is). <channel> is only necessary if the message isn't sent in the channel itself. If <nick> is given, returns the monologue length for that user instead of the caller.

.. _command-supygames-roulette:

``roulette [spin]``
  Fires the revolver. If the bullet was in the chamber, you're dead. Tell me to spin the chambers and I will.

.. _conf-SupyGames:

Configuration
-------------

.. _conf-supybot.plugins.SupyGames.public:


supybot.plugins.SupyGames.public
  This config variable defaults to "True", is not network-specific, and is not channel-specific.

  Determines whether this plugin is publicly visible.

