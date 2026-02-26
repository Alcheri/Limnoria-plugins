# Asyncio

<p align="center">
  <img src="https://img.shields.io/github/v/release/Alcheri/Asyncio?color=blue&sort=semver" alt="Release">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/limnoria-compatible-brightgreen.svg" alt="Limnoria">
  <img src="https://img.shields.io/badge/OpenAI-powered-8A2BE2.svg" alt="OpenAI">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="Licence">
</p>

An asynchronous OpenAI plugin for Limnoria.

## Prerequisites

* Step 1: Create an OpenAI Account [OpenAI Platform]( https://platform.openai.com) 
* Step 2: Generate a New API Key.
* Step 3: Review Pricing and Usage Terms.
* Step 4: Create a file named .env in the root directory of your bot i.e. `~/runbot`.
* Step 5: Add your key-value to this file i.e. `OPENAI_API_KEY = "Your_API_Key"`

## Install

Go into your Limnoria plugin dir, usually ~/runbot/plugins and run:

```plaintext
git clone https://github.com/Alcheri/Asyncio.git
```

To install additional requirements, run from /plugins/Asyncio:

```plaintext
pip install --upgrade -r requirements.txt 
```

Next, load into your bot:

```plaintext
/msg yourbot load Asyncio
```

## Configure your bot

* **_supybot.plugins.Asyncio.botnick \[`your bot's nick`\]_**\
The default is "Assistant".
* **_supybot.plugins.Asyncio.language \[`American, Australian, British or Canadian`\]_**\
The default is "British".

These external modules are required:  ¹ asyncio,  ² openai.

**Note:** The plugin references `OPENAI_API_KEY` as the key-value label.

## Using

```plaintext
@chat good morning
Puss Good morning, SomeNick!  How can I help you today?

@chat Tell me a joke
Puss Processing your message...
Puss Sure thing! Why did the kangaroo cross the road?  
Puss Because it was the chicken’s day off! 🦘😄

@chat What is 3 ** 3?

Puss Processing your message...
Puss 3 ** 3 means 3 raised to the power of 3.
Puss Calculating it:
Puss 3 * 3 * 3 = 27
Puss Final answer: 27

@chat A farm has chickens and cows. There are a total of 50 heads and 130 legs. How many chickens and cows are on the farm?

Puss Processing your message...
Puss Let the number of chickens be C and the number of cows be W.
Puss We have two equations:
Puss 1. C + W = 50 (total heads)
Puss 2. 2C + 4W = 130 (total legs)
Puss From the first equation, we can express W as:
Puss W = 50 - C
Puss Substituting W in the second equation:
Puss 2C + 4(50 - C) = 130
Puss 2C + 200 - 4C = 130
Puss ​-2C + 200 = 130
Puss ​-2C = -70
Puss C = 35
Puss Now, W = 50 - 35 = 15
Puss Final answer: There are 35 chickens and 15 cows.
```

** The plugin handles both arithmetic expressions and equations. It also handles natural language math queries.

**Notes:**

¹ Python's `asyncio` library is a powerful framework designed for writing concurrent code using the async/await syntax.\
&nbsp;&nbsp;It allows you to manage asynchronous I/O operations.

² `openai` is the official Python library for the OpenAI API.

<br><br>
<p align="center">Copyright © MMXXIV, Barry Suridge</p>
