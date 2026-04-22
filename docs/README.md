# TelegramBot

[![GitHub Pages](https://img.shields.io/badge/%20-FFFFFF?style=social&logo=githubpages&logoColor=000000&logoSize=auto)](https://metachannelcorp.github.io/TelegramBot/)
[![GitHub Stars](https://img.shields.io/github/stars/MetaChannelCorp/TelegramBot?style=social&logo=github&logoColor=000000&label=Stars&labelColor=FFFFFF&color=FFFFFF)](https://github.com/MetaChannelCorp/TelegramBot/stargazers)

## Index

1. [Introduction](#introduction)
2. [Project structure](#project-structure)
3. [Clone the repository](#clone-the-repository)
4. [Set up the project](#set-up-the-project)
5. [Create the virtual environment](#create-the-virtual-environment)
5. [Install dependencies](#install-dependencies)
6. [Run it!](#run-it)
7. [Resources](#resources)

## Introduction

A simple Telegram Bot for Odoo!

This project has been developed on a [Linux](https://github.com/torvalds/linux) system. To learn more about the system, visit the [Dotfiles](https://github.com/FJrodafo/Dotfiles) repository.

## Project structure

```
/
├── docs/
│   └── *.md
├── CONTRIBUTING
├── LICENSE
├── .env
├── bot.py
└── requirements.txt
```

## Clone the repository

Open a terminal in the directory where you store your repositories and clone it with the following command:

```shell
# HTTPS
git clone https://github.com/MetaChannelCorp/TelegramBot.git
cd TelegramBot/
```

```shell
# SSH
git clone git@github.com:MetaChannelCorp/TelegramBot.git
cd TelegramBot/
```

## Set up the project

Copy `.env.example` to `.env` and fill the credentials:

```shell
cp .env.example .env
nano .env
```

## Create the virtual environment

```shell
python3 -m venv venv
source venv/bin/activate
```

## Install dependencies

Install the latest stable release of `python-telegram-bot` with the following command:

```shell
pip install python-telegram-bot --upgrade
```

We also need `python-dotenv` to be able to import the environment variables from the `.env` file:

```shell
pip install python-dotenv
```

Export the dependencies installed in the virtual environment with the following command:

```shell
pip freeze > requirements.txt
```

## Run it!

This project is closely linked to another project; before running the Telegram bot, run the Docker service from the [Odoo](https://github.com/MetaChannelCorp/Odoo) repository.

Once the Docker containers from the [Odoo](https://github.com/MetaChannelCorp/Odoo) repository are up and running, you can start the bot with the following command:

```shell
python3 bot/main.py
```

## Resources

[python-telegram-bot](https://python-telegram-bot.org/)
·
[BotFather](https://t.me/BotFather)
·
[userinfobot](https://t.me/userinfobot)
