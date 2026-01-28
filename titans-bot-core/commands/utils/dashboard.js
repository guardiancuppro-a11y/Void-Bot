const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('dashboard')
        .setDescription('Obtenir le lien vers le dashboard de configuration'),
    async execute(interaction) {
        // Remplace par l'URL de ton site déployé (Vercel/Netlify) ou localhost
        const dashboardUrl = 'http://localhost:5173'; 

        const embed = new EmbedBuilder()
            .setTitle('🎛️ Dashboard Titans Bot')
            .setDescription(`Configurez les logs, les événements et les triggers directement depuis le site web.

[**Accéder au Dashboard**](${dashboardUrl})`)
            .setColor('#5865F2');

        await interaction.reply({ embeds: [embed], ephemeral: true });
    },
};
