from cogs.pvp.db import SessionLocal
from sqlalchemy.orm import Session
import discord
from cogs.pvp.models import Duel, DuelStatusEnum, Player

class NewDuelView(discord.ui.View):
    def __init__(self, player1_id):
        super().__init__(timeout=300)
        self.player1_id = player1_id
    
    @discord.ui.button(label="Rejoindre le duel", style=discord.ButtonStyle.primary)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.player1_id:
            await interaction.response.send_message("Tu ne peux pas te défier toi-même tocard !", ephemeral=True)
            return
        session: Session = SessionLocal()
        try:
            for user_id in [self.player1_id, interaction.user.id, 1379017177880854575]:  # 1379017177880854575 is a placeholder for the second player
                if not session.query(Player).filter_by(user_id=str(user_id)).first():
                    print(f"Player {user_id} not found, creating new player.")
                    session.add(Player(user_id=str(user_id)))
                    session.commit()
            session.flush()

            duel = Duel(
                player1_id=str(self.player1_id),
                player2_id=str(interaction.user.id),
                # player2_id=str(1379017177880854575),
                status=DuelStatusEnum.in_progress
            )
            player1 = session.query(Player).filter_by(user_id=str(self.player1_id)).first()
            player2 = session.query(Player).filter_by(user_id=str(interaction.user.id)).first()
            session.add(duel)
            session.commit()
            await interaction.response.send_message(
                f"Player 1 : <@{self.player1_id}>({str(round(player1.elo))}) \nvs\nPlayer 2 : <@{interaction.user.id}>({str(round(player2.elo))})\nDuel en cours...\nUne fois le combat terminé, indiquez le vainqueur :", 
                view=DuelInProgressView(duel.id, player1_id=self.player1_id, player2_id=interaction.user.id),
                ephemeral=False
            )
        except Exception as e:
            print(f"Erreur lors de la création du duel : {e}")
            await interaction.response.send_message("Erreur lors de la création du duel.", ephemeral=True)
            session.rollback()
        finally:
            session.close()
        
class DuelInProgressView(discord.ui.View):
    def __init__(self, duel_id, player1_id=None, player2_id=None):
        super().__init__(timeout=300)
        self.duel_id = duel_id
        self.player1_id = player1_id
        self.player2_id = player2_id
        
    async def winner_calculation(self, interaction, session, duel, winner, loser):
        duel.winner_id = winner.id
        duel.status = DuelStatusEnum.validated
        
        if winner and loser:
            print(f"[DEBUG] Avant update ELO: Winner ELO={winner.elo}, Loser ELO={winner.elo}")
            # Update ELO for both players
            await winner.calculate_duel(loser.elo, "win")
            await loser.calculate_duel(winner.elo, "loss")
            print(f"[DEBUG] Après update ELO: Winner ELO={winner.elo}, Loser ELO={loser.elo}")
            session.add(winner)
            session.add(loser)
        else:
            print("[DEBUG] Un ou plusieurs joueurs introuvables.")
            await interaction.response.send_message("Un ou plusieurs joueurs introuvables.", ephemeral=True)
            return
        session.commit()
        print(f"[DEBUG] Duel validé, victoire de <@{duel.player1_id}> !")
        return winner
    
    @discord.ui.button(label="Player 1", style=discord.ButtonStyle.primary)
    async def player1_win(self, interaction: discord.Interaction, button: discord.ui.Button):
        session: Session = SessionLocal()
        try:
            duel = session.query(Duel).filter_by(id=self.duel_id).first()
            if not duel:
                await interaction.response.send_message("Duel introuvable.", ephemeral=True)
                return
            winner = session.query(Player).filter_by(user_id=duel.player1_id).first()
            if not winner:
                await interaction.response.send_message("Joueur gagnant introuvable.", ephemeral=True)
                return
            print(f"[DEBUG] winner: {winner}")
            loser = session.query(Player).filter_by(user_id=duel.player2_id).first()
            if not loser:
                await interaction.response.send_message("Joueur perdant introuvable.", ephemeral=True)
                return
            print(f"[DEBUG] loser: {loser}")
            
            await self.winner_calculation(interaction, session, duel, winner, loser)
            
            await interaction.response.send_message(f"Victoire de <@{duel.player1_id}> !", ephemeral=False)
            
        except Exception as e:
            print(f"[DEBUG] Erreur lors de la validation du duel : {e}")
            await interaction.response.send_message("Erreur lors de la validation du duel.", ephemeral=True)
            session.rollback()
        finally:
            session.close()

    @discord.ui.button(label="Player 2", style=discord.ButtonStyle.primary)
    async def player2_win(self, interaction: discord.Interaction, button: discord.ui.Button):
        session: Session = SessionLocal()
        try:
            duel = session.query(Duel).filter_by(id=self.duel_id).first()
            if not duel:
                await interaction.response.send_message("Duel introuvable.", ephemeral=True)
                return
            winner = session.query(Player).filter_by(user_id=duel.player2_id).first()
            if not winner:
                await interaction.response.send_message("Joueur gagnant introuvable.", ephemeral=True)
                return
            print(f"[DEBUG] winner: {winner}")
            loser = session.query(Player).filter_by(user_id=duel.player1_id).first()
            if not loser:
                await interaction.response.send_message("Joueur perdant introuvable.", ephemeral=True)
                return
            print(f"[DEBUG] loser: {loser}")
            
            await self.winner_calculation(interaction, session, duel, winner, loser)
            
            await interaction.response.send_message(f"Victoire de <@{winner.user_id}> !", ephemeral=False)
            
        except Exception as e:
            print(f"[DEBUG] Erreur lors de la validation du duel : {e}")
            await interaction.response.send_message("Erreur lors de la validation du duel.", ephemeral=True)
            session.rollback()
        finally:
            session.close()

class PvpMenuView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id
    
    @discord.ui.button(label="Mes duels", style=discord.ButtonStyle.primary)
    async def my_duels(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Tu ne peux pas voir les duels d'un autre utilisateur !", ephemeral=True)
            return
        session: Session = SessionLocal()
        duels = session.query(Duel).filter(
            (Duel.player1_id == str(self.user_id)) | (Duel.player2_id == str(self.user_id))
        ).all()
        if not duels:
            await interaction.response.send_message("Aucun duel trouvé pour cet utilisateur.", ephemeral=True)
            session.close()
            return
        
        embed = discord.Embed(title="Mes duels", color=discord.Color.blue())
        for duel in duels:
            embed.add_field(
                name=f"Duel ID: {duel.id}",
                value=f"Joueur 1: <@{duel.player1_id}>\nJoueur 2: <@{duel.player2_id}>\nStatut: {duel.status.value}\nDate de création: {duel.date_creation.strftime('%Y-%m-%d %H:%M:%S')}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        session.close()

    @discord.ui.button(label="Mes stats", style=discord.ButtonStyle.primary)
    async def my_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Tu ne peux pas voir les stats d'un autre utilisateur !", ephemeral=True)
            return
        session: Session = SessionLocal()
        player = session.query(Player).filter_by(user_id=str(self.user_id)).first()
        if not player:
            await interaction.response.send_message("Aucun joueur trouvé pour cet utilisateur.", ephemeral=True)
            session.close()
            return
        embed = discord.Embed(title="Mes stats", color=discord.Color.green())
        embed.add_field(name="Elo", value=str(round(player.elo)), inline=True)
        embed.add_field(name="Victoires", value=str(player.wins), inline=True)
        embed.add_field(name="Défaites", value=str(player.losses), inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        session.close()