# Discord Team Manager Bot

A Discord bot designed to manage team-based events, tournaments, and signups.  
It provides a clean, interactive UI using Discord buttons, modals, and views — allowing users to enlist as players, become captains, create teams, invite players, remove players, and disband teams.

This bot requires no external database.  
All state is stored using Discord roles and channels.

---

## Features

### **Signup System**
- **Become Captain** — opens a modal to create a new team.
- **Enlist as Player** — assigns the Player role.
- **Unenlist** — removes the user from the event or disbands their team if they are a captain.

### **Team Creation**
When a captain creates a team:
- A **Team \<Name\>** role is created.
- A private text channel is created for the team.
- The captain receives:
  - Team role
  - Player role
  - Captain role
- A **Team Management Panel** is posted inside the team channel.

### **Team Management Panel**
Displayed inside each team’s private channel:
- **Invite Player** — captains can invite free agents to join their team.
- **Remove Player** — captains can remove players from their team.

### **Invite System**
Players receive a DM with:
- **Accept Invite** — joins the team.
- **Decline Invite** — notifies the captain.

### **Team Disbanding**
If a captain unenlists:
- All team members lose the team role.
- The team role is deleted.
- The team channel is deleted.
- The captain loses Captain + Player roles.

---

## Project Structure

Discord-Team-Manager/
│
├── bot.py                # Main bot entry point
├── src/
│   ├── commands.py       # Slash command setup (e.g., /setup_signup)
│   ├── views.py          # All UI logic (SignupView, TeamNameModal, TeamManagementView, etc.)
│   └── init.py
│
└── .venv/                # Python virtual environment


---

Discord Team Manager Bot
Deployment and Usage Instructions
---------------------------------

1. Description
   The Discord Team Manager Bot handles team-based event organization inside a Discord server.
   Users can enlist as players, become captains, create teams, invite players, remove players,
   and disband teams. All data is stored using Discord roles and channels. No database is required.

2. Requirements
   - Python 3.12 or newer
   - discord.py 2.3 or newer
   - A Discord bot token
   - A Discord server where the bot has permission to manage roles and channels

3. Installation
   3.1 Clone your project repository.
   3.2 Create a virtual environment:
       python -m venv .venv
   3.3 Activate the virtual environment:
       Windows: .venv\Scripts\activate
       Linux/macOS: source .venv/bin/activate
   3.4 Install dependencies:
       pip install discord.py

4. Bot Token Setup
   4.1 Go to https://discord.com/developers/applications
   4.2 Create a new application.
   4.3 Add a bot to the application.
   4.4 Enable the following intents:
       - Server Members Intent
       - Message Content Intent (optional)
   4.5 Copy your bot token.
   4.6 Open bot.py and set:
       TOKEN = "YOUR_BOT_TOKEN_HERE"

5. Invite the Bot to Your Server
   5.1 In the Developer Portal, open OAuth2 → URL Generator.
   5.2 Select:
       - bot
       - applications.commands
   5.3 Under bot permissions, enable:
       - Manage Roles
       - Manage Channels
       - Send Messages
       - Read Message History
   5.4 Copy the generated URL and open it in your browser.
   5.5 Invite the bot to your server.

6. Running the Bot Locally
   6.1 Activate your virtual environment.
   6.2 Run the bot:
       python bot.py
   6.3 You should see:
       Logged in as Team Manager Bot

7. Usage Instructions
   7.1 In your Discord server, run the slash command:
       /setup_signup
       This posts the signup panel.

   7.2 Players click “Enlist as Player” to join the event.

   7.3 Users who want to lead a team click “Become Captain” and submit a team name.

   7.4 When a team is created:
       - A Team <Name> role is created.
       - A private team channel is created.
       - The captain receives Captain, Player, and Team roles.
       - A Team Management Panel is posted inside the team channel.

   7.5 Inside the team channel, captains can:
       - Invite players to join their team.
       - Remove players from their team.

   7.6 Players receive a DM when invited:
       - Accept Invite → joins the team
       - Decline Invite → captain is notified

   7.7 If a captain clicks “Unenlist”, their entire team is disbanded:
       - All members lose the team role
       - The team role is deleted
       - The team channel is deleted
       - The captain loses Captain and Player roles

8. Deploying on a Linux Server
   8.1 Copy your project to the server.
   8.2 Create and activate a virtual environment.
   8.3 Install discord.py.
   8.4 Run:
       python bot.py

9. Optional: Run as a Background Service (systemd)
   9.1 Create a service file:
       sudo nano /etc/systemd/system/team-manager.service

   9.2 Paste the following:
       [Unit]
       Description=Discord Team Manager Bot
       After=network.target

       [Service]
       User=ubuntu
       WorkingDirectory=/home/ubuntu/Discord-Team-Manager
       ExecStart=/home/ubuntu/Discord-Team-Manager/.venv/bin/python bot.py
       Restart=always

       [Install]
       WantedBy=multi-user.target

   9.3 Enable and start the service:
       sudo systemctl enable team-manager
       sudo systemctl start team-manager

10. Notes
    - The bot must have Manage Roles and Manage Channels permissions.
    - The bot’s highest role must be above Player, Captain, and all Team roles.
    - No database is required; everything is handled through Discord roles and channels.
