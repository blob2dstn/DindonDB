from db import SessionLocal
from sqlalchemy.orm import Session
import discord
from pvp.models import Duel, DuelStatusEnum, Player

class DuelView(discord.ui.View):
    def __init__(self, player1_id):
        super().__init__(timeout=300)
        self.player1_id = player1_id
    
    @discord.ui.button(label="Rejoindre le duel", style=discord.ButtonStyle.primary)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.player1_id:
            await interaction.response.send_message("Tu ne peux pas te défier toi-même tocard !", ephemeral=True)
            return
        session: Session = SessionLocal()
        for user_id in [self.player1_id, interaction.user.id]:
            if not session.query(Player).filter_by(id=str(user_id)).first():
                session.add(Player(id=str(user_id)))
                
        duel = Duel(
            player1_id=str(self.player1_id),
            player2_id=str(interaction.user.id),
            status = DuelStatusEnum.in_progress.value
        )
        
        session.add(duel)
        session.commit()
        await interaction.response.send_message(
            f"<@{self.player1_id}> vs <@{interaction.user.id}> ! Duel en cours. Le gagnant peut taper '/victoire'.",
            ephemeral=False
        )
        self.disable_all_items()
        await interaction.message.edit(view=self)
        session.close()