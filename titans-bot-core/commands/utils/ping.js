const { SlashCommandBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('ping')
        .setDescription('Vérifier la latence du bot'),
    async execute(interaction) {
        await interaction.reply(`🏓 Pong! Latence: ${Date.now() - interaction.createdTimestamp}ms`);
    },
};
