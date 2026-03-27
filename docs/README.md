# MetaBot

[![GitHub Pages](https://img.shields.io/badge/%20-white?style=social&logo=githubpages&logoColor=black&logoSize=auto)](https://fjrodafo.github.io/MetaBot/)
[![GitHub Stars](https://img.shields.io/github/stars/FJrodafo/MetaBot?style=social&logo=github&logoColor=black&label=Stars&labelColor=white&color=white)](https://github.com/FJrodafo/MetaBot/stargazers)

## Index

1. [Introduction](#introduction)
2. [Clone the repository](#clone-the-repository)
3. [Set up the project](#set-up-the-project)
4. [Create the virtual environment](#create-the-virtual-environment)
5. [Install the dependencies](#install-the-dependencies)
6. [Resources](#resources)

## Introduction

A simple Telegram Bot for Odoo CRM!

This project has been developed on a [Linux](https://github.com/torvalds/linux) system. To learn more about the system, visit the [Dotfiles](https://github.com/FJrodafo/Dotfiles) repository.

```
/
├── .env
├── bot.py
└── requirements.txt
```

## Clone the repository

Open a terminal in the directory where you store your repositories and clone it with the following command:

```shell
# HTTPS
git clone https://github.com/FJrodafo/MetaBot.git
```

```shell
# SSH
git clone git@github.com:FJrodafo/MetaBot.git
```

## Set up the project

Copy `.env.example` to `.env` and fill the credentials:

```shell
cp .env.example .env
```

## Create the virtual environment

```shell
python3 -m venv venv
source venv/bin/activate
```

## Install the dependencies

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

## Resources

[python-telegram-bot](https://python-telegram-bot.org/)
