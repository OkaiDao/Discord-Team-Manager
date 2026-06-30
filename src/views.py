import discord
from discord.ext import commands


class SignupView(discord.ui.View):
    """
    Main signup panel for the event.
    Allows users to become captains, enlist as players, or unenlist.
    """

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Become Captain",
        style=discord.ButtonStyle.primary,
        custom_id="signup_captain"
    )
    async def become_captain(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Assigns Captain and Player roles immediately, then opens the team creation modal.
        Users who already belong to a team cannot become captains.
        """
        guild = interaction.guild

        for role in interaction.user.roles:
            if role.name.startswith("Team "):
                return await interaction.response.send_message(
                    "You already have a team. Captains can only create one team.",
                    ephemeral=True
                )

        captain_role = discord.utils.get(guild.roles, name="Captain")
        if captain_role is None:
            captain_role = await guild.create_role(name="Captain")

        player_role = discord.utils.get(guild.roles, name="Player")
        if player_role is None:
            player_role = await guild.create_role(name="Player")

        if captain_role not in interaction.user.roles:
            await interaction.user.add_roles(captain_role)

        if player_role not in interaction.user.roles:
            await interaction.user.add_roles(player_role)

        modal = TeamNameModal()
        await interaction.response.send_modal(modal)


    @discord.ui.button(
        label="Enlist as Player",
        style=discord.ButtonStyle.success,
        custom_id="signup_player"
    )
    async def enlist_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Assigns the Player role to users who are not already enlisted.
        """
        guild = interaction.guild
        player_role = discord.utils.get(guild.roles, name="Player")

        if player_role is None:
            player_role = await guild.create_role(name="Player")

        if player_role in interaction.user.roles:
            return await interaction.response.send_message(
                "You are already enlisted as a Player.",
                ephemeral=True
            )

        await interaction.user.add_roles(player_role)
        await interaction.response.send_message(
            "You have been enlisted as a Player.",
            ephemeral=True
        )

    @discord.ui.button(
        label="Unenlist",
        style=discord.ButtonStyle.danger,
        custom_id="unenlist"
    )
    async def unenlist(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Handles player unenlisting and captain team disbanding logic.
        """
        guild = interaction.guild
        user = interaction.user

        player_role = discord.utils.get(guild.roles, name="Player")
        captain_role = discord.utils.get(guild.roles, name="Captain")

        if player_role not in user.roles:
            return await interaction.response.send_message(
                "You are not enlisted as a Player.",
                ephemeral=True
            )

        team_role = None
        for role in user.roles:
            if role.name.startswith("Team "):
                team_role = role
                break

        is_captain = captain_role in user.roles if captain_role else False

        if team_role is None:
            await user.remove_roles(player_role)
            return await interaction.response.send_message(
                "You have been unenlisted from the event.",
                ephemeral=True
            )

        if not is_captain:
            await user.remove_roles(team_role)
            return await interaction.response.send_message(
                f"You have been removed from {team_role.name}.",
                ephemeral=True
            )

        for member in guild.members:
            if team_role in member.roles:
                await member.remove_roles(team_role)

        team_name = team_role.name.replace("Team ", "")
        prefix = team_name.lower().replace(" ", "-")

        for channel in guild.channels:
            if channel.name.startswith(prefix):
                try:
                    await channel.delete()
                except:
                    pass

        await team_role.delete()

        if is_captain:
            await user.remove_roles(captain_role)

        await user.remove_roles(player_role)

        await interaction.response.send_message(
            "Your team has been disbanded and you have been unenlisted.",
            ephemeral=True
        )


class TeamNameModal(discord.ui.Modal, title="Create Your Team"):
    """
    Modal used by captains to create a new team.
    Handles role creation, channel creation, and captain role assignment.
    """

    team_name = discord.ui.TextInput(
        label="Team Name",
        placeholder="Enter your team name",
        max_length=32
    )

    def __init__(self):
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        """
        Creates the team role, private team channel, and assigns captain/player roles.
        """
        guild = interaction.guild
        captain = interaction.user
        name = self.team_name.value

        existing = discord.utils.get(guild.roles, name=f"Team {name}")
        if existing:
            return await interaction.response.send_message(
                f"A team named **{name}** already exists.",
                ephemeral=True
            )

        team_role = await guild.create_role(
            name=f"Team {name}",
            reason="Creating team role for new captain"
        )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            team_role: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(
            f"{name.lower().replace(' ', '-')}-chat",
            overwrites=overwrites,
            reason="Private team text channel"
        )

        view = TeamManagementView(team_role)
        await channel.send(
            f"**{team_role.name} Management Panel**",
            view=view
        )

        await captain.add_roles(team_role)

        player_role = discord.utils.get(guild.roles, name="Player")
        if player_role is None:
            player_role = await guild.create_role(name="Player")
        await captain.add_roles(player_role)

        captain_role = discord.utils.get(guild.roles, name="Captain")
        if captain_role is None:
            captain_role = await guild.create_role(name="Captain")
        await captain.add_roles(captain_role)

        await interaction.response.send_message(
            f"Team **{name}** created successfully!",
            ephemeral=True
        )


class TeamManagementView(discord.ui.View):
    """
    Management panel displayed inside each team's private channel.
    Allows captains to invite players or remove team members.
    """

    def __init__(self, team_role: discord.Role):
        super().__init__(timeout=None)
        self.team_role = team_role

    async def interaction_is_captain(self, interaction: discord.Interaction):
        """
        Returns True if the interacting user is a captain.
        """
        captain_role = discord.utils.get(interaction.guild.roles, name="Captain")
        return captain_role in interaction.user.roles

    @discord.ui.button(
        label="Invite Player",
        style=discord.ButtonStyle.primary,
        custom_id="team_invite"
    )
    async def invite_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Opens a player selection menu for captains to send team invitations.
        """
        if not await self.interaction_is_captain(interaction):
            return await interaction.response.send_message(
                "Only the captain can invite players.",
                ephemeral=True
            )

        guild = interaction.guild
        player_role = discord.utils.get(guild.roles, name="Player")

        free_agents = []
        for member in guild.members:
            if member == interaction.user:
                continue
            if player_role in member.roles:
                if not any(r.name.startswith("Team ") for r in member.roles):
                    free_agents.append(member)

        if not free_agents:
            return await interaction.response.send_message(
                "No available players to invite.",
                ephemeral=True
            )

        options = [
            discord.SelectOption(label=m.display_name, value=str(m.id))
            for m in free_agents
        ]

        select = InviteSelect(options, self.team_role, interaction.user)
        view = discord.ui.View()
        view.add_item(select)

        await interaction.response.send_message(
            "Select a player to invite:",
            view=view,
            ephemeral=True
        )

    @discord.ui.button(
        label="Remove Player",
        style=discord.ButtonStyle.danger,
        custom_id="team_remove"
    )
    async def remove_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Opens a selection menu allowing captains to remove players from their team.
        """
        if not await self.interaction_is_captain(interaction):
            return await interaction.response.send_message(
                "Only the captain can remove players.",
                ephemeral=True
            )

        guild = interaction.guild

        team_members = [
            m for m in guild.members
            if self.team_role in m.roles and
            "Captain" not in [r.name for r in m.roles]
        ]

        if not team_members:
            return await interaction.response.send_message(
                "No players to remove.",
                ephemeral=True
            )

        options = [
            discord.SelectOption(label=m.display_name, value=str(m.id))
            for m in team_members
        ]

        select = RemoveSelect(options, self.team_role)
        view = discord.ui.View()
        view.add_item(select)

        await interaction.response.send_message(
            "Select a player to remove:",
            view=view,
            ephemeral=True
        )


class InviteSelect(discord.ui.Select):
    def __init__(self, options, team_role, captain):
        super().__init__(placeholder="Choose a player", options=options)
        self.team_role = team_role
        self.captain = captain

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        player_id = int(self.values[0])
        player = guild.get_member(player_id)

        view = InviteResponseView(self.team_role, self.captain, player, guild)

        try:
            await player.send(
                f"You have been invited to join **{self.team_role.name}** by {self.captain.display_name}.",
                view=view
            )
            await interaction.response.send_message(
                f"Invite sent to {player.display_name}.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                f"Could not DM {player.display_name}. They may have DMs disabled.",
                ephemeral=True
            )


class InviteResponseView(discord.ui.View):
    """
    Invite response panel shown to players.
    Allows them to accept or decline a team invitation.
    """

    def __init__(self, team_role, captain, player, guild):
        super().__init__(timeout=None)
        self.team_role = team_role
        self.captain = captain
        self.player = player
        self.guild = guild

    @discord.ui.button(label="Accept Invite", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Adds the player to the team if they accept the invitation.
        """
        if interaction.user.id != self.player.id:
            return await interaction.response.send_message(
                "This invite is not for you.",
                ephemeral=True
            )

        member = self.guild.get_member(self.player.id)
        if member is None:
            return await interaction.response.send_message(
                "Could not verify your membership in the server.",
                ephemeral=True
            )

        if any(r.name.startswith("Team ") for r in member.roles):
            return await interaction.response.send_message(
                "You are already on a team.",
                ephemeral=True
            )

        await member.add_roles(self.team_role)

        await interaction.response.send_message(
            f"You have joined **{self.team_role.name}**!",
            ephemeral=True
        )

        try:
            await self.captain.send(
                f"{member.display_name} has accepted your invite."
            )
        except:
            pass

    @discord.ui.button(label="Decline Invite", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Notifies the captain that the player declined the invitation.
        """
        if interaction.user.id != self.player.id:
            return await interaction.response.send_message(
                "This invite is not for you.",
                ephemeral=True
            )

        await interaction.response.send_message(
            "You declined the invite.",
            ephemeral=True
        )

        try:
            await self.captain.send(
                f"{self.player.display_name} has declined your invite."
            )
        except:
            pass


class RemoveSelect(discord.ui.Select):
    """
    Dropdown menu allowing captains to select a player to remove from their team.
    """

    def __init__(self, options, team_role):
        super().__init__(placeholder="Choose a player", options=options)
        self.team_role = team_role

    async def callback(self, interaction: discord.Interaction):
        """
        Removes the selected player from the team.
        """
        guild = interaction.guild
        player_id = int(self.values[0])
        player = guild.get_member(player_id)

        await player.remove_roles(self.team_role)

        await interaction.response.send_message(
            f"{player.mention} has been removed from **{self.team_role.name}**.",
            ephemeral=True
        )
